# ADR-006: Automated Code Remediation Architecture

**Status**: Accepted
**Date**: 2024-12-11
**Deciders**: Platform Architecture Team, M7 Working Group

## Context

Government agencies and contractors often have legacy codebases with 50-200 CVEs per application. Manual remediation is time-consuming (weeks to months), error-prone, and blocks FedRAMP ATO approval.

**Problem Statement**:

- Manual dependency upgrades take 2-4 hours per application
- Breaking changes in major version upgrades cause production incidents
- Dockerfile hardening requires deep security expertise
- No automated way to generate ATO-compliant code

**M7 Goal**:
Enable "one-click remediation" where users bring vulnerable code and Aegis generates:

- Hardened Dockerfile (Chainguard base images)
- Upgraded dependencies (zero-CVE versions)
- Rebuilt application with passing tests
- Git pull request with changes
- Before/After SBOM comparison

## Decision

We will implement **AI-assisted automated code remediation** with the following architecture:

### 1. Remediation Engine Components

```
User Repository (GitHub/GitLab)
    ↓
Aegis Remediation API
    ├─> Language Detector (Node.js, Python, Java, Go, Ruby)
    ├─> Dependency Parser (package.json, requirements.txt, pom.xml, etc.)
    ├─> Vulnerability Mapper (CVE → Fixed Version resolver)
    ├─> Dockerfile Generator (Chainguard base image selection)
    ├─> Dependency Upgrader (smart version bumping with semver analysis)
    ├─> Build Validator (ephemeral container build + test execution)
    └─> PR Generator (git commit + push + PR creation)
```

### 2. Language Support Matrix

| Language | Dependency Files                       | Package Manager     | SBOM Tool |
| -------- | -------------------------------------- | ------------------- | --------- |
| Node.js  | package.json, package-lock.json        | npm, yarn, pnpm     | Syft      |
| Python   | requirements.txt, poetry.lock, Pipfile | pip, poetry, pipenv | Syft      |
| Java     | pom.xml, build.gradle                  | Maven, Gradle       | Syft      |
| Go       | go.mod, go.sum                         | go modules          | Syft      |
| Ruby     | Gemfile, Gemfile.lock                  | bundler             | Syft      |

### 3. Dependency Upgrade Logic

**Smart Version Resolution**:

```typescript
interface DependencyUpgrade {
  packageName: string;
  currentVersion: string;
  vulnerabilities: Vulnerability[];
  fixedVersion: string; // Minimum version with zero CVEs
  latestVersion: string; // Latest stable version
  breakingChanges: boolean; // Detected via semver major version bump
  confidence: 'high' | 'medium' | 'low'; // Upgrade safety score
}

async function resolveDependencyUpgrades(
  dependencies: Dependency[],
  vulnerabilities: Vulnerability[]
): Promise<DependencyUpgrade[]> {
  const upgrades: DependencyUpgrade[] = [];

  for (const dep of dependencies) {
    const depVulns = vulnerabilities.filter(
      (v) => v.packageName === dep.name && v.packageVersion === dep.version
    );

    if (depVulns.length === 0) {
      continue; // No vulnerabilities, skip
    }

    // Find minimum version that fixes all CVEs
    const fixedVersion = await findMinimumFixedVersion(dep.name, depVulns);

    // Check for breaking changes
    const breakingChanges = isBreakingChange(dep.version, fixedVersion);

    // Calculate confidence score
    const confidence = calculateUpgradeConfidence(
      dep,
      fixedVersion,
      breakingChanges
    );

    upgrades.push({
      packageName: dep.name,
      currentVersion: dep.version,
      vulnerabilities: depVulns,
      fixedVersion,
      latestVersion: await getLatestVersion(dep.name),
      breakingChanges,
      confidence,
    });
  }

  return upgrades;
}

function calculateUpgradeConfidence(
  dep: Dependency,
  fixedVersion: string,
  breakingChanges: boolean
): 'high' | 'medium' | 'low' {
  // High confidence: Patch or minor version bump
  if (!breakingChanges && semver.diff(dep.version, fixedVersion) !== 'major') {
    return 'high';
  }

  // Medium confidence: Major version but within same major.x
  if (
    breakingChanges &&
    semver.major(dep.version) === semver.major(fixedVersion)
  ) {
    return 'medium';
  }

  // Low confidence: Multiple major versions jump
  return 'low';
}
```

### 4. Dockerfile Generation

**Template-Based Generation**:

```typescript
interface DockerfileTemplate {
  language: string;
  baseImage: string;
  buildCommands: string[];
  runtimeCommands: string[];
}

const templates: Record<string, DockerfileTemplate> = {
  nodejs: {
    language: 'Node.js',
    baseImage: 'cgr.dev/chainguard/node:latest',
    buildCommands: [
      'FROM cgr.dev/chainguard/node:latest-dev AS builder',
      'WORKDIR /app',
      'COPY package*.json ./',
      'RUN npm ci --only=production',
      'COPY . .',
      'RUN npm run build',
    ],
    runtimeCommands: [
      'FROM cgr.dev/chainguard/node:latest',
      'WORKDIR /app',
      'COPY --from=builder /app/dist ./dist',
      'COPY --from=builder /app/node_modules ./node_modules',
      'COPY package.json ./',
      'USER 65532',
      'EXPOSE 3000',
      'CMD ["node", "dist/index.js"]',
    ],
  },
  python: {
    language: 'Python',
    baseImage: 'cgr.dev/chainguard/python:latest',
    buildCommands: [
      'FROM cgr.dev/chainguard/python:latest-dev AS builder',
      'WORKDIR /app',
      'COPY requirements.txt .',
      'RUN pip install --user --no-cache-dir -r requirements.txt',
      'COPY . .',
    ],
    runtimeCommands: [
      'FROM cgr.dev/chainguard/python:latest',
      'WORKDIR /app',
      'COPY --from=builder /home/nonroot/.local /home/nonroot/.local',
      'COPY --from=builder /app .',
      'ENV PATH=/home/nonroot/.local/bin:$PATH',
      'USER 65532',
      'EXPOSE 8000',
      'CMD ["python", "app.py"]',
    ],
  },
};

function generateDockerfile(language: string, config: AppConfig): string {
  const template = templates[language];
  if (!template) {
    throw new Error(`Unsupported language: ${language}`);
  }

  const dockerfile = [
    `# Generated by Aegis Automated Remediation`,
    `# Base image: ${template.baseImage} (Zero CVEs)`,
    ``,
    ...template.buildCommands,
    ``,
    ...template.runtimeCommands,
  ].join('\n');

  return dockerfile;
}
```

### 5. Build Validation

**Ephemeral Build Environment**:

```typescript
import Docker from 'dockerode';

interface BuildValidationResult {
  success: boolean;
  buildLogs: string;
  testResults?: TestResult;
  imageDigest?: string;
  errorMessage?: string;
}

async function validateBuild(
  repository: GitRepository,
  dockerfile: string,
  upgradedDependencies: DependencyUpgrade[]
): Promise<BuildValidationResult> {
  const docker = new Docker();

  try {
    // 1. Create ephemeral build environment
    const tarStream = createTarball(
      repository,
      dockerfile,
      upgradedDependencies
    );

    // 2. Build image
    const buildStream = await docker.buildImage(tarStream, {
      t: `aegis-remediation-${repository.name}:${Date.now()}`,
      pull: false,
      buildargs: { BUILDKIT: '1' },
    });

    const buildLogs = await collectBuildLogs(buildStream);

    // 3. Run tests (if test command exists)
    const testResults = await runTests(docker, repository);

    // 4. Generate SBOM and scan
    const sbom = await generateSBOM(imageDigest);
    const scanResults = await scanVulnerabilities(imageDigest);

    // 5. Validate zero CVEs
    if (scanResults.criticalCount > 0 || scanResults.highCount > 0) {
      return {
        success: false,
        buildLogs,
        errorMessage: `Build succeeded but found ${scanResults.criticalCount} critical and ${scanResults.highCount} high CVEs`,
      };
    }

    return {
      success: true,
      buildLogs,
      testResults,
      imageDigest,
    };
  } catch (error) {
    return {
      success: false,
      buildLogs: error.message,
      errorMessage: `Build failed: ${error.message}`,
    };
  } finally {
    // Cleanup: Remove ephemeral containers and images
    await cleanupBuildArtifacts(docker);
  }
}
```

### 6. Pull Request Generation

**Git Integration**:

```typescript
import { Octokit } from '@octokit/rest';

async function createRemediationPR(
  repository: GitRepository,
  changes: RemediationChanges,
  validationResult: BuildValidationResult
): Promise<PullRequest> {
  const octokit = new Octokit({ auth: process.env.GITHUB_TOKEN });

  // 1. Create feature branch
  const branchName = `aegis/remediation-${Date.now()}`;
  await octokit.git.createRef({
    owner: repository.owner,
    repo: repository.name,
    ref: `refs/heads/${branchName}`,
    sha: repository.headSha,
  });

  // 2. Commit changes
  const files = [
    { path: 'Dockerfile', content: changes.dockerfile },
    { path: 'package.json', content: changes.packageJson },
    { path: 'package-lock.json', content: changes.packageLockJson },
  ];

  for (const file of files) {
    await octokit.repos.createOrUpdateFileContents({
      owner: repository.owner,
      repo: repository.name,
      path: file.path,
      message: `chore: aegis automated remediation - ${file.path}`,
      content: Buffer.from(file.content).toString('base64'),
      branch: branchName,
    });
  }

  // 3. Create PR
  const prBody = generatePRDescription(changes, validationResult);

  const pr = await octokit.pulls.create({
    owner: repository.owner,
    repo: repository.name,
    title: '🛡️ Aegis: Automated Security Remediation',
    head: branchName,
    base: repository.defaultBranch,
    body: prBody,
  });

  return pr.data;
}

function generatePRDescription(
  changes: RemediationChanges,
  validation: BuildValidationResult
): string {
  return `
## 🛡️ Aegis Automated Security Remediation

This PR was automatically generated by Aegis to remediate security vulnerabilities in your application.

### Summary
- **CVEs Fixed**: ${changes.vulnerabilities.length}
- **Dependencies Upgraded**: ${changes.upgrades.length}
- **Build Status**: ${validation.success ? '✅ Passed' : '❌ Failed'}
- **Test Status**: ${validation.testResults?.success ? '✅ All tests passed' : '⚠️ See details'}

### Vulnerability Remediation
| CVE ID | Package | Current Version | Fixed Version | Severity |
|--------|---------|-----------------|---------------|----------|
${changes.vulnerabilities
  .map(
    (v) =>
      `| ${v.cveId} | ${v.packageName} | ${v.currentVersion} | ${v.fixedVersion} | ${v.severity} |`
  )
  .join('\n')}

### Dependency Upgrades
${changes.upgrades
  .map(
    (u) =>
      `- **${u.packageName}**: ${u.currentVersion} → ${u.fixedVersion} ${u.breakingChanges ? '⚠️ Major version' : '✅ Safe'}`
  )
  .join('\n')}

### Dockerfile Changes
- ✅ Switched to Chainguard base image (\`${changes.chainguardImage}\`)
- ✅ Multi-stage build for minimal runtime image
- ✅ Non-root user (UID 65532)
- ✅ No shell or package manager in runtime

### SBOM Comparison
**Before**: ${changes.sbomBefore.packageCount} packages, ${changes.sbomBefore.cveCount} CVEs
**After**: ${changes.sbomAfter.packageCount} packages, ${changes.sbomAfter.cveCount} CVEs

**CVE Reduction**: ${changes.sbomBefore.cveCount - changes.sbomAfter.cveCount} vulnerabilities eliminated ✅

### Next Steps
1. Review the changes in this PR
2. Verify tests pass (CI pipeline will run automatically)
3. Merge when ready to deploy hardened application

---
*Generated by [Aegis DevSecOps Platform](https://aegis.dso.mil) - FedRAMP ATO Automation*
`;
}
```

### 7. User Workflow (UI)

```typescript
// React component
function RemediationDashboard() {
  const [repositories, setRepositories] = useState<Repository[]>([]);

  const handleAutomatedRemediation = async (repo: Repository) => {
    // 1. Trigger remediation
    const result = await api.post('/api/v1/remediation/analyze', {
      repositoryUrl: repo.url,
      branch: repo.defaultBranch,
    });

    // 2. Display proposed changes
    setProposedChanges(result.data);

    // 3. User reviews and approves
    // 4. API creates PR
  };

  return (
    <div>
      <h2>Automated Code Remediation</h2>
      {repositories.map(repo => (
        <RepositoryCard
          key={repo.id}
          repository={repo}
          cveCount={repo.cveCount}
          onRemediate={() => handleAutomatedRemediation(repo)}
        />
      ))}
    </div>
  );
}
```

## Consequences

### Positive

✅ **Time savings**: Remediation time reduced from weeks to minutes
✅ **Accuracy**: Eliminates human error in dependency upgrades
✅ **Safety**: Build validation prevents broken deployments
✅ **Transparency**: Pull request provides full visibility into changes
✅ **Scalability**: Can remediate 50+ repositories per day
✅ **ATO acceleration**: Automated evidence generation speeds FedRAMP approval

### Negative

❌ **False positives**: May propose upgrades that break application logic
❌ **Test coverage dependency**: Requires existing test suite to validate changes
❌ **AI model cost**: LLM usage for changelog analysis adds operational cost
❌ **Complexity**: Sophisticated system with many failure modes
❌ **Trust barrier**: Users may be skeptical of automated code changes

### Neutral

⚖️ **Human oversight**: Users still review and approve PRs (not fully autonomous)
⚖️ **Incremental rollout**: Can start with low-confidence upgrades disabled

## Alternatives Considered

### Alternative 1: Dependabot / Renovate Bot (status quo)

**Rejected**: Only upgrades dependencies, does not fix Dockerfiles. No build validation. Creates 20+ PRs per repo (noisy).

### Alternative 2: Manual remediation by security team

**Rejected**: Does not scale. Average 2-4 weeks per application. Bottleneck for ATO.

### Alternative 3: AI code generation (fully autonomous)

**Rejected**: Too risky without human review. Cannot guarantee correctness.

## Implementation Notes

- M7 implementation (Weeks 35-42)
- Support Node.js, Python, Java, Go, Ruby (5 languages minimum)
- GitHub and GitLab integration (Bitbucket future)
- Terraform manages ephemeral build workers (Kubernetes Jobs)
- Prometheus metrics: remediation success rate, CVE reduction, build times

## References

- [Dependabot Documentation](https://docs.github.com/en/code-security/dependabot)
- [Renovate Bot](https://docs.renovatebot.com/)
- [Chainguard Images](https://images.chainguard.dev/)
- [Syft SBOM Tool](https://github.com/anchore/syft)
- [Grype Vulnerability Scanner](https://github.com/anchore/grype)
