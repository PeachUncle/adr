# Architecture Decision Record (ADR): Conception et Génération de la Carte

## Context

### Justification de l'ADR
Le module Map est au cœur de l'application et définit l'environnement dans lequel évoluent les robots. Actuellement, la carte est générée à partir d'un seed et enrichie par une série de modificateurs (par exemple, `add_base` et `add_random_elements`) qui ajoutent des éléments essentiels comme la base, des ressources minérales, de l'énergie et des points d'intérêt. Cet ADR documente les choix architecturaux adoptés dans l'état actuel du projet.

### Approche de conception
L'implémentation actuelle repose sur une fonction centrale `generate_map(width, height, seed, modifiers)` qui :
- Génère une grille de base en fonction des dimensions déterminées par la taille du terminal et du seed défini dans `config.toml`.
- Applique successivement des fonctions de modification pour enrichir la carte avec les éléments nécessaires au gameplay.
  Cette approche modulaire permet de conserver une logique simple et cohérente dans la génération et la modification de la carte.

## Proposed design

### Services/Modules Impactés
- **Module Map** : Gère la génération et la modification de la carte.
- **Module UI** : Utilise la carte pour l'affichage et l'interaction utilisateur.
- **Module Robot** : Se base sur la carte pour la navigation et les interactions dans l'environnement.

### Nouveaux Services/Modules
Aucun nouveau module n'a été ajouté. L'approche s'appuie sur les fonctions existantes pour la création et la modification de la carte.

### Impact sur le Modèle et les DTO
Le modèle de la carte est constitué d'une grille de tuiles, chaque tuile possédant un type spécifique (base, minéral, énergie, intérêt). Ce modèle est directement exploité par les modules UI et Robot pour afficher et interagir avec l'environnement de jeu.

### Impact sur les API
Le module Map expose une API interne simple et directe :
- La fonction `generate_map` permet de créer la carte en se basant sur les paramètres de configuration.
- Les fonctions de modification appliquées à la carte constituent l'interface utilisée par les autres modules sans complexité superflue.

### Impact sur la configuration générale
Le fichier `config.toml` contient des paramètres essentiels (comme le seed et éventuellement des dimensions) qui assurent la reproductibilité et la cohérence de la génération de la carte. Ces paramètres sont utilisés directement par le module Map.

### Impact DevOps
L'intégration de la génération de la carte dans le processus d'exécution ne nécessite pas d'outils supplémentaires. La configuration actuelle permet d'obtenir un environnement de développement cohérent avec l'état de production sans surcroit d'outillage.

## Considerations

### Alternatives
- Générer la carte de manière entièrement procédurale sans appliquer de modificateurs séquentiels.
- Intégrer une bibliothèque externe dédiée à la génération de terrains pour gérer la complexité de manière différente.

### Concerns
- La complexité potentielle liée à l'application séquentielle de plusieurs modificateurs.
- La performance lors de la génération de cartes de grandes dimensions.

### Résolution des Concerns
L'approche actuelle répond aux besoins fonctionnels sans complexifier le code. Les performances et la simplicité de l'algorithme se sont avérées suffisantes pour les scénarios envisagés dans l'état actuel du projet.

## Decision

### Important implementation Detail
La carte est générée par l'appel à la fonction `generate_map(width, height, seed, modifiers)`, qui applique une série de modificateurs dans l'ordre défini pour ajouter la base et d'autres éléments essentiels.

### Caveats
Le mécanisme actuel ne gère pas de manière avancée les interactions ou les conflits potentiels entre différents modificateurs. Ce choix est jugé acceptable dans le cadre des besoins immédiats.

### Future considerations
Si les besoins du projet évoluent (par exemple, pour des cartes de très grande taille ou des interactions complexes entre modificateurs), une réévaluation de l'approche de génération pourra être envisagée.

### Remaining or Deferred Design Issues
L'optimisation des performances pour des cartes à très haute densité n'a pas été traitée, car le besoin ne s'est pas encore présenté dans l'état actuel du projet.

## References
- [ADR: Choose UI](choose-ui.md) (pour la structure générale et le choix de l'interface utilisateur)
- Documentation interne du projet (README.md, config.toml)
- Code source du module Map (répertoire `src/map/`)
