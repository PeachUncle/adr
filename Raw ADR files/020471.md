# 3. WIP Use XXX for macOS defaults as code

Date: 2025-12-11

## Status

Draft

Implements [2. Configure macOS defaults as code](0002-configure-macos-defaults-as-code.md)

## Context

## Options

- [8ta4/plist][plist] keeps an eye on changes in plist files and spits out
  PlistBuddy commands when you update preferences in macOS or apps
  (Haskell).
- [geerlingguy/mac-dev-playbook][mdp] executes an [.osx][] script that 
  runs `defaults write` commands (Ansible, Shell).
- [dsully/macos-defaults][dsmd] manages macOS defaults declaratively via 
  YAML files (Rust).
- [brokosz/macos-default][brmd] exports/imports macOS defaults to/from 
  plist files (Shell).
- [tarranjones/macOS-defaults][tjmd] NPM module to access the macOS
  defaults system (Javascript).
- [WillAbides/plist-diff][pdiff] watches a directory tree and reports 
  changes to stdout every 2 seconds (Go).
- [catilac/PlistWatch][pwatch] monitors real-time changes to plist files and 
  outputs defaults commands to recreate changes (Go).
- [Wilfred/difftastic][difft] is a structural diff tool that compares files 
  based on their syntax, including YAML (Rust).
- [sters/diffnest][diffnest] compares JSON, YAML, and other structured data 
  files with an intuitive unified diff output (Go). 

## Deliberation

### Architecture considerations

#### Mechanisms

From the `defaults` man page: 

```
Preferences are stored in a set of files under ~/Library/Preferences,
however using the defaults command is much safer than manually
editing a .plist file. The cfprefsd daemon manages and caches updates
to preference files. If you modify the file directly, the changes
will not propagate through the cache managed by the daemon.  
```

So there's a delay between changing preferences and the corresponding
plist file updates in the file system. Solutions that rely on
monitoring files for and reporting on changes are likely to be both
laggy and larger-batchy, picking up a bunch of unrelated changes
rather than discrete, intentional configuration changes.

#### Paradigms of configuration management

While I'm fond of true [immutable infrastructure][cncf-ii] — erase
everything and start from scratch anytime you want to make a change
— a more practical solution for a "daily driver" Mac is to rebuild
seasonally. As such, I favor configuration as code and idempotence, 
while facilitating a fairly smooth and speedy full rebuild. 

### Assays

#### Assay 1: DSully macos-defaults bookends with YAML diff

Try running `[macos-defaults][dsmd]` before and after changes, using a
YAML diff tool to see what's changed.

After a quick search, `[difftastic][difft]` appears to be an active 
project that compares YAML files and has a Homebrew formula.

##### Findings

Unfortunately, DSully's macos-defaults tool reads plist files rather
than interacting with cfprefsd, so it's going to get laggy, chunky
results.

#### Assay 2: 

## Decision

## Consequences

What becomes easier or more difficult to do and any risks introduced
by the change that will need to be mitigated.

[plist]: https://github.com/8ta4/plist (plist by 8ta4 on GitHub)
[mdp]: https://github.com/geerlingguy/mac-dev-playbook (mac-dev-playbook by Jeff Geerling on GitHub)
[.osx]: https://github.com/geerlingguy/dotfiles/blob/master/.osx
[dsmd]: https://github.com/dsully/macos-defaults (macos-defaults by dsully on GitHub)
[brmd]: https://github.com/brokosz/macos-defaults (macos-defaults by Brad Rokosz on GitHub)
[tjmd]: https://github.com/tarranjones/macOS-defaults (macOS-defaults by Tarran Jones on GitHub)
[pdiff]: https://github.com/WillAbides/plist-diff (plist-diff by WillAbides on GitHub)
[pwatch]: https://github.com/catilac/plistwatch (PlistWatch by Moon on GitHub)
[cncf-ii]: https://glossary.cncf.io/immutable-infrastructure/ (Immutable infrastructure by Cloud Native Compute Federation)
[diffnest]: https://github.com/sters/diffnest?tab=readme-ov-file (diffnest by sters on GitHub)
[difft]: https://github.com/Wilfred/difftastic (difftastic by Wilfred Hughes on GitHub)
