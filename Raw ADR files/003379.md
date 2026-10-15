# ADR-003: Central Graph System Architecture

**Status**: Accepted and Implemented  
**Date**: October 2025  
**Decision Makers**: Development Team  
**Related Documents**: 
- `docs/active-development/CENTRAL_GRAPH_ROADMAP.md`
- `docs/core-foundation.md`

---

## Context

Protogen's initial architecture used scene-specific graph nodes and edges (`scene_nodes`, `scene_edges`) for each scene's presentational layer. While this provided flexibility, it created several challenges as the system evolved:

### Problems with Scene-Specific Graph Data

1. **Data Duplication**: Same nodes duplicated across multiple scenes
2. **Complex Traversal**: Difficult to query relationships across scenes
3. **Performance Issues**: Excessive joins for multi-scene graph operations
4. **Maintenance Overhead**: Updates to shared nodes required multi-table modifications
5. **Unclear Boundaries**: Confusion between canonical data and presentational instances
6. **Limited Reusability**: Hard to share graph structures between scenes

### Requirements

- Single source of truth for all graph data
- Efficient graph traversal and querying
- Support for logical groupings of nodes (subgraphs)
- Spatial positioning for all scene types (not just graphs)
- Maintain excellent multi-tenant, snapshot, and scene type systems
- Backward compatibility during transition
- Performance optimization through caching

---

## Decision

**We will implement a Central Graph System with subgraphs and enhanced scene items**, replacing scene-specific node/edge tables with a centralized architecture.

### Central Graph Architecture

```
Central Graph (Single Source of Truth)
├── CoreGraphNode (canonical node data)
├── CoreGraphEdge (canonical edge data with weights)
└── Presentation Layer
    ├── Subgraph System (logical node groupings)
    │   ├── Subgraph (metadata and ownership)
    │   └── SubgraphNode (pivot for node membership)
    └── Scene Items (spatial positioning for all types)
        ├── Node items (references to CoreGraphNode)
        ├── Edge items (references to CoreGraphEdge)
        └── Other items (text, image, video, etc.)
```

### Key Design Principles

1. **Single Source of Truth**: All canonical graph data in `core_graph_nodes` and `core_graph_edges`
2. **Subgraphs for Organization**: Logical groupings of nodes for efficient traversal
3. **Scene Items for Presentation**: Spatial positioning and styling for all scene types
4. **Scene Type Optimization**:
   - Graph scenes → Use subgraphs for node sets
   - Card/Document scenes → Use scene items for spatial layout
5. **Tenant Isolation**: Subgraphs and scene items respect tenant boundaries
6. **Performance**: Subgraph-based caching and lazy loading

---

## Consequences

### Positive

✅ **Single Source of Truth**: Eliminates data duplication  
✅ **Better Performance**: Optimized queries with subgraph caching  
✅ **Easier Traversal**: Simple graph operations across all scenes  
✅ **Flexible Grouping**: Subgraphs can be shared or tenant-specific  
✅ **Universal Positioning**: Scene items work for all scene types  
✅ **Cleaner Architecture**: Clear separation between data and presentation  
✅ **Scalability**: Efficient handling of large graphs  
✅ **Maintainability**: Updates to nodes propagate automatically

### Negative

⚠️ **Migration Required**: Existing scene-specific data needs transformation  
⚠️ **More Complex Queries**: Some queries require joins through pivot tables  
⚠️ **Breaking Change**: Scene-specific tables removed (fresh start approach)

### Neutral

ℹ️ **Table Renaming**: `core_graph_*` simplified to standard naming  
ℹ️ **New Models**: Subgraph and SceneItem models added  
ℹ️ **API Evolution**: New endpoints for subgraph management

---

## Implementation Details

### Database Schema

#### Core Graph Tables
```sql
-- Canonical node data
CREATE TABLE nodes (
    id BIGSERIAL PRIMARY KEY,
    guid UUID UNIQUE NOT NULL,
    node_type_id BIGINT,
    label VARCHAR(255),
    meta JSONB,
    position JSONB,  -- Stored positions for persistence
    is_active BOOLEAN DEFAULT true
);

-- Canonical edge data
CREATE TABLE edges (
    id BIGSERIAL PRIMARY KEY,
    guid UUID UNIQUE NOT NULL,
    source_node_id BIGINT REFERENCES nodes(id),
    target_node_id BIGINT REFERENCES nodes(id),
    edge_type_id BIGINT,
    weight NUMERIC DEFAULT 1.0,
    meta JSONB,
    is_active BOOLEAN DEFAULT true
);
```

#### Subgraph System
```sql
-- Logical groupings of nodes
CREATE TABLE subgraphs (
    id BIGSERIAL PRIMARY KEY,
    guid UUID UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    tenant_id BIGINT REFERENCES tenants(id),
    is_public BOOLEAN DEFAULT false
);

-- Subgraph membership
CREATE TABLE subgraph_nodes (
    id BIGSERIAL PRIMARY KEY,
    subgraph_id BIGINT REFERENCES subgraphs(id) ON DELETE CASCADE,
    node_id BIGINT REFERENCES nodes(id) ON DELETE CASCADE,
    UNIQUE(subgraph_id, node_id)
);
```

#### Scene Items (Spatial Positioning)
```sql
-- Universal scene item system
CREATE TABLE scene_items (
    id BIGSERIAL PRIMARY KEY,
    scene_id BIGINT REFERENCES scenes(id) ON DELETE CASCADE,
    item_type VARCHAR(50) NOT NULL,  -- node, edge, text, image, video
    item_id BIGINT,  -- Reference to node/edge/other
    item_guid UUID,
    position JSONB,  -- {x, y, z} coordinates
    dimensions JSONB,  -- {width, height}
    style JSONB,  -- Scene-specific styling
    meta JSONB,
    is_visible BOOLEAN DEFAULT true,
    z_index INTEGER DEFAULT 0
);
```

### Scene Type Patterns

#### Graph Scenes
```typescript
// Use subgraph for node set
const scene = await Scene.create({
    scene_type: 'graph',
    subgraph_id: subgraph.id,  // Reference to subgraph
    // ...
});

// Get nodes via subgraph
const nodes = await scene.subgraph.nodes;
```

#### Card/Document Scenes
```typescript
// Use scene items for spatial layout
const sceneItem = await SceneItem.create({
    scene_id: scene.id,
    item_type: 'node',
    item_id: node.id,
    position: { x: 100, y: 200 },
    dimensions: { width: 150, height: 100 }
});
```

---

## Migration Strategy

### Approach: Fresh Start

Given the fundamental architectural change, we opted for a fresh start rather than complex data migration:

1. **Clear Existing Data**: Truncate scene-specific tables
2. **Create Default Subgraphs**: Seed with example subgraphs
3. **Update Scene Models**: Add subgraph relationships
4. **Rebuild Scenes**: Use new architecture for all new content

### Backward Compatibility

During transition, the Scene service maintains compatibility:

```php
public function getSceneNodes(Scene $scene) {
    if ($scene->subgraph_id) {
        // New architecture
        return $scene->subgraph->nodes;
    } else {
        // Legacy fallback
        return $scene->items()->where('item_type', 'node')->get();
    }
}
```

---

## Implementation Status

### Completed (October 2025)

- ✅ Database migrations for subgraphs and scene items
- ✅ Subgraph and SceneItem models
- ✅ API endpoints for subgraph CRUD
- ✅ Scene Items API endpoints
- ✅ Graph Studio integration with subgraph management
- ✅ Node position persistence in JSON field
- ✅ Mouse event handling improvements (drag/context menu)
- ✅ Feature branch merged to main

### Deferred

- ⏳ Force-directed layout algorithms
- ⏳ Layout presets and templates
- ⏳ Advanced subgraph sharing system
- ⏳ Scene navigation modularization
- ⏳ Enhanced authoring tools

---

## Alternatives Considered

### Alternative 1: Keep Scene-Specific Tables

**Approach**: Maintain scene_nodes and scene_edges with better optimization

**Rejected Because**:
- Doesn't solve fundamental duplication problem
- Complex multi-table queries for cross-scene operations
- Maintenance overhead continues to grow
- Missed opportunity for cleaner architecture

### Alternative 2: Full Graph Database (Neo4j)

**Approach**: Replace PostgreSQL with dedicated graph database

**Rejected Because**:
- Major infrastructure change
- Loss of PostgreSQL JSONB and other features
- Additional complexity in multi-tenant setup
- Unnecessary for current scale

### Alternative 3: Hybrid Approach

**Approach**: Keep some scene-specific tables for "phantom" nodes

**Rejected Because**:
- Increases complexity without clear benefit
- Confusing mental model
- Scene items provide same functionality more cleanly

---

## Success Metrics

### Technical Metrics (Achieved)

✅ Subgraph queries < 100ms  
✅ Support for 1000+ nodes per subgraph  
✅ Proper tenant isolation maintained  
✅ Graph Studio drag-and-drop functional  

### Functional Metrics

✅ Graph scenes render via subgraphs  
✅ Scene items support spatial positioning  
✅ Node position persistence working  
✅ Context menus and interactions functional  

---

## References

- **Roadmap**: `docs/active-development/CENTRAL_GRAPH_ROADMAP.md`
- **Core Foundation**: `docs/core-foundation.md`
- **Implementation**: `api/app/Models/Subgraph.php`, `api/app/Models/SceneItem.php`
- **Frontend**: `shared/src/systems/graph-studio/`

---

## Notes

The Central Graph System represents a significant architectural evolution that simplifies graph operations while maintaining the excellent multi-tenant, snapshot, and scene type systems. The fresh start approach allowed for a clean implementation without legacy baggage.

The decision to implement subgraphs for logical grouping and scene items for spatial positioning provides flexibility for all current and future scene types.

**Key Insight**: Separating canonical graph data from presentational concerns was the right architectural choice, even though it required a fresh start.

