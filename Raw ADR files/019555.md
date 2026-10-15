# ADR-003: gRPC for Trip-Driver Internal Communication

**Status:** Accepted  
**Date:** October 2025  
**Decision Makers:** Ngô Quang Tiến, Không Huỳnh Ngọc Hân  

---

## Context

The Trip Service and Driver Service need to communicate frequently for:
- Finding nearby available drivers when a trip is requested
- Notifying drivers of new trip requests
- Updating trip status when driver accepts

This communication is **latency-sensitive** and **high-frequency**.

---

## Decision Drivers

1. **Latency**: Critical user path (passenger waits for driver assignment)
2. **Type Safety**: Prevent contract mismatches between services
3. **Performance**: Handle 100+ req/sec between services
4. **Development Complexity**: Learning curve, debugging difficulty

---

## Considered Options

### Option 1: REST/HTTP JSON
**Pros:**
- ✅ Simple, familiar to team
- ✅ Easy debugging (cURL, Postman)
- ✅ Text-based (human-readable)

**Cons:**
- ❌ **Higher latency**: ~100ms round-trip (measured)
- ❌ No type safety across services
- ❌ Larger payload size (JSON vs Protobuf)

### Option 2: gRPC (CHOSEN)
**Pros:**
- ✅ **⚡ Low latency**: ~40ms round-trip (60% faster than REST)
- ✅ **Type safety**: Shared .proto definitions
- ✅ Binary protocol (Protobuf) = smaller payloads
- ✅ Supports streaming (future: live location updates)
- ✅ Native NestJS support

**Cons:**
- ❌ **Complex setup**: Proto file generation, build pipeline
- ❌ Harder debugging (binary protocol)
- ❌ Steeper learning curve

### Option 3: Message Queue (RabbitMQ)
**Pros:**
- ✅ Asynchronous, decoupled

**Cons:**
- ❌ **Not suitable**: Passenger needs **immediate** response, not eventual consistency

---

## Decision Outcome

**Chosen:** **gRPC** (Option 2) **ONLY for Trip ↔ Driver communication**

### Rationale

1. **Critical Latency Path:**
   - User is **actively waiting** for driver assignment
   - Every 50ms saved improves perceived performance
   - **40ms vs 100ms** = **60% latency reduction**

2. **Type Safety:**
   - Proto definitions prevent API contract drift
   - Compile-time errors instead of runtime failures
   ```protobuf
   service DriverService {
     rpc FindNearbyDrivers(LocationRequest) returns (DriversResponse);
   }
   ```

3. **Measured Performance:**
   | Metric | gRPC | REST | Improvement |
   |--------|------|------|-------------|
   | Latency | 40ms | 100ms | 60% faster |
   | Payload | 150 bytes | 400 bytes | 62% smaller |

### Trade-off Accepted

| Cost | Benefit | Decision |
|------|---------|----------|
| Complex build setup (proto gen) | 60% latency reduction | **Worth it** for critical path |
| Harder debugging | Type safety prevents bugs | **Worth it** for production reliability |
| Team learning curve | Better performance for users | **Worth it** for UX |

### Limited Scope

**Important:** gRPC is ONLY used for Trip ↔ Driver.

**Other services use REST** because:
- API Gateway ↔ Services: REST (public-facing, easier debugging)
- Auth ↔ User: TCP/REST (not latency-critical)
- Most internal calls: REST (simplicity > performance)

This **pragmatic approach** balances performance where it matters with simplicity elsewhere.

---

## Implementation

**Proto Definition:**
```protobuf
syntax = "proto3";

package driver;

service DriverService {
  rpc FindNearbyDrivers (LocationRequest) returns (DriversResponse);
  rpc NotifyDriver (TripRequest) returns (DriverResponse);
}

message LocationRequest {
  double latitude = 1;
  double longitude = 2;
  double radius_km = 3;
  string vehicle_type = 4;
}

message DriversResponse {
  repeated Driver drivers = 1;
}

message Driver {
  string driver_id = 1;
  double distance_km = 2;
  string name = 3;
  string vehicle_plate = 4;
}
```

**Trip Service (gRPC Client):**
```typescript
@Injectable()
export class TripService {
  @Inject('DRIVER_SERVICE')
  private readonly driverClient: ClientGrpc;

  async findNearbyDrivers(lat: number, lng: number) {
    const driverService = this.driverClient.getService<DriverService>('DriverService');
    return await lastValueFrom(
      driverService.findNearbyDrivers({
        latitude: lat,
        longitude: lng,
        radiusKm: 5,
        vehicleType: 'car'
      })
    );
  }
}
```

**Driver Service (gRPC Server):**
```typescript
@Controller()
export class DriverController {
  @GrpcMethod('DriverService', 'FindNearbyDrivers')
  async findNearbyDrivers(data: LocationRequest): Promise<DriversResponse> {
    const drivers = await this.driverService.findNearby(
      data.latitude,
      data.longitude,
      data.radiusKm
    );
    return { drivers };
  }
}
```

---

## Challenges Encountered

**Problem 1:** Initial gRPC setup error
```
Error: 12 UNIMPLEMENTED: The server does not implement the method FindNearbyDrivers
```

**Root Cause:** Proto file path mismatch in Nx monorepo

**Solution:**
- Centralize proto files in `libs/shared/src/lib/protos/`
- Generate TypeScript with `--ts_proto_opt=nestJs=true`
- Import from shared library in both services

**Problem 2:** Port conflicts

**Solution:** Use separate ports for gRPC (5001, 5002) and REST (3000-3005)

---

## Validation

**Load Test Results:**
- **Setup:** 100 concurrent trip requests
- **gRPC:** 40ms avg latency, 0 errors
- **REST (comparison):** 95ms avg latency, 2 timeouts
- **Conclusion:** gRPC is **2.4x faster** and more reliable

---

## Future Enhancements

1. **Bi-directional streaming**: Real-time driver location updates to Trip Service
2. **Load balancing**: Use gRPC load balancer when scaling to multiple Driver Service instances
3. **Monitoring**: Add gRPC interceptors for latency tracking

---

## References

1. [gRPC Official Docs](https://grpc.io/docs/)
2. [NestJS gRPC](https://docs.nestjs.com/microservices/grpc)
3. [Protobuf Language Guide](https://developers.google.com/protocol-buffers/docs/proto3)

---

**Status:** ✅ ACCEPTED  
**Next Review:** When adding service mesh (Istio)
