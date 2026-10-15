<script type="module">
  import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid@11/dist/mermaid.esm.min.mjs';
</script>

# ADR-002: [TCNP] traitement et mode d'exposition

- Status: accepted
- Date: 2023-10-10

## Context and Problem Statement
*contexte et énoncé du problème*

Effectuer la correspondance d'identités entre les données de l'INSEE (RNIP) et les données d'un système tiers métiers. Les critères de recherche sont limitées au nom, prénom, date de naissance et lieu de naissance.

Les données sont mises à jour mensuellement par l'INSEE qui les met à disposition entre le 1er et 15 de chaque mois depuis un portail accessible par login/password


**système** :

- est accessible en interne de l'entreprise;
- doit servir une seule application métier rapidement par rapport au contexte sportif;
- authentifier l'application métier

**volumétrie prévue** :

- plus de 300 000 changements d'identités (initialement prévu 70 000);
- 2 millions d'enquêtes annuelles

**contraintes** :

- format des données différent entre les données sources (présence de tirets, d'apostrophes) et les données métiers (absence de tiret, d'aspostrohe);
- le mode de requêtage se construit de manière itérative et doit être pour l'instant très adaptables.
  

Faut-il intégrer des principes de recherches approximatives et de scoring ?
   
## Decision Drivers
*facteurs de décisions*

Faute de développeurs (internet/externe) il est nécessaire de minimiser au maximum le développement compte tenu des délais pour une mise en production et une homologation en décembre 2023.

L'application doit être maintenue par la service Team.

## Considered Options
*options envisagées*

  - option 1 : API et données en mémoire (ex: utilisation de pandas, polar)
    - avantages : s3 est le seul point de stockage;
    - inconvénients : empreinte mémoire importante compte tenu de l'évolution de la volumétrie  

<pre class="mermaid">
graph LR;
  client([client])-. Ingress-managed <br> load balancer .->ingress[Ingress,https://api];
  ingress-->|/api/v1/identites|service1[Service api-ci];
  s3-->|load-data|cronjob
  cronjob --> service2[service load data]
  subgraph cluster
  ingress;
  service1-->pod1[Pod];
  service1-->pod2[Pod];
  service1-->pod3[Pod];
  service2 --> pod4[Pod];
  service2 --> pod5[Pod];
  cronjob --> pod6[Pod];
  end
  
  classDef plain fill:#ddd,stroke:#fff,stroke-width:4px,color:#000;
  classDef k8s fill:#326ce5,stroke:#fff,stroke-width:4px,color:#fff;
  classDef cluster fill:#fff,stroke:#bbb,stroke-width:2px,color:#326ce5;
  class ingress,service1,service2,pod1,pod2,pod3,pod4,pod5,pod6 k8s;
  class client plain;
  class cluster cluster;
</pre>

- option 2 : API et elasticsearch/opensearch
  
    - avantages : recherche approchante en utilisant la méthode de recherche par distance (*jaro-winkler* ou *levenshtein*);
    - inconvénients: définir un seuil et une méthode de scoring
   
 <pre class="mermaid">
graph LR;
    s3-->cronjob;
    cronjob-->opensearch;
 
 </pre>
> note: chargement des données

<pre class="mermaid">
graph LR;
  client([client])-. Ingress-managed <br> load balancer .->ingress_es[Ingress,https://api-es];
  ingress_es -->|/api/v1/identites|service4[Service api-ci-es];
  subgraph cluster
  ingress_es;
  service3-->pod4[Pod];
  service3-->pod5[Pod];
  service3-->pod6[Pod];
  service4-->pod9[Pod];
  service4-->pod10[Pod];
  service4-->pod11[Pod];
  pod9-->service3[Service opensearch]
  end
  
  classDef plain fill:#ddd,stroke:#fff,stroke-width:4px,color:#000;
  classDef k8s fill:#326ce5,stroke:#fff,stroke-width:4px,color:#fff;
  classDef cluster fill:#fff,stroke:#bbb,stroke-width:2px,color:#326ce5;
  class ingress_es,ingress_opensearch,service3,service4,pod4,pod5,pod6,pod7,pod8,pod9,pod10,pod11 k8s;
  class client plain;
  class cluster cluster;

</pre>

  - option 3 : La base de base de données directement exposée via postgrest https://postgrest.org/en/v11/.
    - avantages :
      - rapidité de mise en oeuvre;
      - accepte nativement les recherches de type égal (*.eq*) ou contient (*.like* ou *.ilike*) 
    - inconvénients : 
      - préparation de données (noms, prénoms) spécifiques aux ré-utilisateurs
      - format de requêtage des api non standards

## Decision Outcome
*Résultat de la décision*

  **L'option numéro 3 est choisie.**

## Consequences

La prise en compte de nouveaux consommateurs de l'API nécessite l'ajout de nouvelles données préparées et adaptées aux consommateurs.
