# ADR: Organize Robots

## Context

### Justification de l'ADR
Les robots représentent l'élément dynamique central de l'application. Ils interagissent avec la carte pour explorer, collecter des ressources et réaliser diverses actions. L'organisation actuelle du module, réparti sur plusieurs fichiers (par exemple, `collector.rs`, `explorator.rs`, `robot.rs`, `robot_type.rs`, `scientist.rs`), vise à clarifier les responsabilités et à faciliter la compréhension du comportement de chaque type de robot.

### Approche de conception
L'approche actuelle consiste à segmenter le code en fonction des différents types de robots et de leurs fonctionnalités spécifiques, tout en centralisant les comportements communs dans des fichiers partagés. Cette organisation permet :
- Une séparation claire des responsabilités pour chaque type de robot.
- Une meilleure lisibilité et facilité de maintenance du code.
- Un accès direct aux spécificités de chaque comportement sans complexifier un seul fichier.

---

## Proposed design

### Services/Modules Impactés
- **Module Robot** : Gère l'initialisation, le comportement et l'interaction des robots avec l'environnement.
- **Module Map** : Fournit les informations environnementales nécessaires à la navigation des robots.
- **Module UI** : Affiche l'état et les actions des robots dans l'interface utilisateur.

### Nouveaux Services/Modules
Aucun nouveau module n'a été introduit. L'organisation repose sur la structuration existante en plusieurs fichiers dédiés aux différents aspects et types de robots.

### Impact sur le Modèle et les DTO
- Le modèle des robots est défini dans des fichiers spécifiques et s'appuie sur une énumération (dans `robot_type.rs`) pour distinguer les différents types.
- Les Data Transfer Objects (DTO) utilisés pour communiquer l'état des robots vers les autres modules (UI, Map) sont simples et reflètent directement la structure des robots telle qu'implémentée.

### Impact sur les API
- Le module Robot expose des fonctions internes permettant la création et la mise à jour des états des robots.
- L'API reste simple, sans couche d'abstraction supplémentaire, ce qui correspond à l'état actuel du projet.

### Impact sur la configuration générale
- Aucun paramètre spécifique de configuration n'est dédié aux robots. Leur comportement dépend principalement du code et des interactions définies dans le module.
- La configuration globale (via `config.toml`) n'affecte pas directement l'implémentation des robots.

### Impact DevOps
- L'organisation en plusieurs fichiers facilite la gestion du code source et l'intégration continue en permettant des tests ciblés et une compilation modulaire.
- Aucune modification particulière du pipeline DevOps n'est nécessaire, car le système actuel reste inchangé dans son fonctionnement.

---

## Considerations

### Alternatives
- **Centralisation** : Regrouper tout le code relatif aux robots dans un seul fichier pour simplifier la navigation, au risque de rendre le code moins lisible et difficile à maintenir.
- **Abstraction supplémentaire** : Introduire des traits ou des patterns de conception (comme Strategy) pour gérer dynamiquement les comportements des différents types de robots, ce qui pourrait être excessif dans l'état actuel du projet.

### Concerns
- Risque de duplication de logique si certains comportements communs ne sont pas correctement centralisés.
- La multiplication des fichiers peut rendre la navigation dans le module moins intuitive pour les nouveaux contributeurs.

### Résolution des Concerns
- La séparation actuelle permet déjà de distinguer clairement les comportements spécifiques des robots tout en réutilisant des fonctions communes.
- Une documentation claire au sein du module et dans le README du projet peut aider à la compréhension de la structure existante.

---

## Decision

### Important implementation Detail
L'organisation du module Robot repose sur une structure multi-fichier où chaque type de robot est défini dans son propre fichier (par exemple, `collector.rs`, `explorator.rs`, `scientist.rs`) et les comportements communs sont centralisés dans `robot.rs` et `robot_type.rs`.

### Caveats
L'approche actuelle ne prévoit pas de mécanisme d'abstraction plus poussé (par exemple, via des traits), ce qui pourrait limiter l'extensibilité en cas de complexification des comportements des robots.

### Future considerations
Si les besoins évoluent pour gérer des comportements plus complexes ou des interactions concurrentes entre robots, une refonte de l'architecture pourrait être envisagée pour introduire des abstractions supplémentaires.

### Remaining or Deferred Design Issues
La gestion fine de la concurrence ou de la synchronisation entre robots n'est pas abordée dans l'état actuel du projet. Cette question pourra être traitée ultérieurement si le besoin se fait sentir.

---

## References
- [ADR: Choose UI](choose-ui.md) (pour la structure globale et les choix d'interface)
- Code source du module Robot (répertoire `src/robot/`)
- Documentation interne du projet (README.md, config.toml)
