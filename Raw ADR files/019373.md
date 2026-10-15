# Domain Objects

## Status

accepted (trial)

## Context

When dealing with **strict** [^1] domain objects we encounter the issue, that we need many projections.

An example to illustrate that:

```java
// DTO (only controller layer
record CreatePizzaDto(
                String name,
                Option<String> description,
                float price
        ) {
}

// main domain model - model aims to be as helpful as possible with solving our business problem
public record Pizza(
        int id,
        @NonNull String name,
        @NonNull Option<String> description,
        float price
) {
}

// Object that the repository & consequently database can work with
public record PersistablePizza(
        // no id needed bc. db-generated
        @NonNull String name,
        @NonNull Option<String> description,
        int priceInCents // better to persist than float
) {
}
```

These are our main objects (one for each of our controller, domain & persistence-layer).
But in between these we might have a lot of other 'in-between' states.

For example:

```markdown
- PlaceOrderDto is taken with its main properties being orderDetails, addressDescription and orderer property
- the addressDescription is enhanced with latitude, longitude by a GpsService introducing a new object/class called
  AddressDescriptionWithLatLong
- the orderer needs to be checked in the db and we might want to add the UUID if the user is already registered (-> also
  new class for this object)
- the addressDescriptionWithLatLong gets persisted and now has an database-generated id which we need to transport back
  to our facade/service (-> does the combined object need a new class??)
- we need to find a chef and a delivery_driver from our db and enhance our in-between object (oh boy it's pretty
  convoluted already...)
```

When we create tight types and avoid a generic Order class where everything can be null or god forbid even
an `HashMap<String, Object>` with mutations all over the codebase, then we quickly run into issues where
a lot of objects and boilerplate might be created to stick with "pure" functions. [^2]

Let's summarize this approach:

- We don't care about duplicate code, just create a Record/class for every interface or use-case

| Approach                            | Positive                                                | Negative                                      |
|-------------------------------------|---------------------------------------------------------|-----------------------------------------------|
| Duplicate code                      | no tight coupling; more muscle-training for the fingers | it's easy to loose track of what's going on   |
| Use inheritance for the projections | less finger-work                                        | tight coupling; inheritance is just the worst |

What other option we have?

- just use arguments and Tuples in order to have multiple return types like:

```java
class MyServiceImpl implements MyService {
    public Tuple4<UUID, Integer, String, String> createOrder(UUID ordererId, Map<Integer, Integer> pizzaIdToQuantity, String destinationCity, String destinationStreet, String destinationHouse, int zipCode, ...
}
```

| Tool                                     | Positive                               | Negative                                                                      |
|------------------------------------------|----------------------------------------|-------------------------------------------------------------------------------|
| Replace Objects with primitive arguments | no tight coupling; no useless objects; | it's easy to loose track of what's going on; it's easy to mess things up [^3] |

When we look at typescript for example there would be no such issue because we could:

```ts
type UserId = UUID;
type Latitude = number;
type Longitude = number;

function createOrder(userId: UserId, lat: Latitude, long: Longitude): {createdOrderId: number, ...} {
  ...
}
```

So why don't we do the same thing with Objects?

```java
public record PizzaId(int id) {
    public static PizzaId fromInt(int id) {
        return new PizzaId(id);
    }

    public int toInt() {
        return id;
    }
}

public record PizzaName(@NonNull String value) {
    public static PizzaName fromString(@NonNull String value) {
        return new PizzaName(value);
    }

    public String toString() {
        return value;
    }
}

public record PizzaDescription(@NonNull Option<String> value) {
    public static PizzaDescription fromNullableString(String value) {
        return new PizzaDescription(Option.of(value));
    }

    public static PizzaDescription fromOption(Option<String> value) {
        return new PizzaDescription(value);
    }

    public String toNullableString() {
        return value.getOrNull();
    }

    public Option<String> toOption() {
        return value;
    }
}

public record Price(int inEuroCent) {
    @Override
    public String toString() {
        double inEuro = inEuroCent / 100.0;
        NumberFormat formatter = NumberFormat.getCurrencyInstance(Locale.GERMANY);
        return formatter.format(inEuro);
    }

    /** eg. 125 -> 12,50€ */
    public static Price fromEuroCents(int euroCents) {
        return new Price(euroCents);
    }

    /** eg. 12.5 -> 12,50€ */
    public static Price fromEuros(float euros) {
        return Price.fromEuroCents(Math.round(euros * 100));
    }
}
```

used like:

```java
    public Tuple4<PizzaId, PizzaName, PizzaDescription, Price> createOrder(PizzaName name,PizzaDescription desc,Price price){...
```

Yes it is verbose and the boxing and unboxing is probably quite bad for the runtime, but for 99.99% of the cases runtime
don't matter and we could always optimize later.

The benefit though is, that we know what goes in and we know what comes out [^4]. And we can combine everything as we
need
to, because each object is literally a single property of our domain object!

## Decision

* Try Atomic-Property-Objects [^5] to deal with the issue of composability and duplicate code
* Since mapping is done on each object we can probably get rid of the Service layer in 99% of the cases [^6] [^7]

## Consequences

| Profit/Price | Description                                                                                                           |
|--------------|-----------------------------------------------------------------------------------------------------------------------|
| PROFIT       | We are more flexible in how we pass data around and keep the meaning of each building transparent & well documented . |
| PRICE        | We gonna deal with a lot of classes and boxing/unboxing.                                                              |
| PROFIT       | We are still open to use some sensical Object for in between state, but it's not our only tool to get the job done.   |
| PRICE        | If we mix Atomic-Property-Objects and Projections the codebase could get a bit inconsistent.                          |

### Footnotes

* [^1]: strict = immutable mostly which consequently means non-null
* [^2]: One could argue here that main issue is, that objects in general are not a great tool to deal with this kind of
  problems, but that's a bit of a heated discussion and fact is that:
    * Java is as OOP as it gets, where everything is an object, which is essentially your only tool to get the job done
    * sometimes you just gotta play the cards that you're dealt (sorry no rust, f#, scala, or functional programming in
      any other form 😭)
* [^3]: `public void getDestination(long latitude, long longitude)` it's sooo easy to accidentally invoke the function
  like `service.getDestination(longitude, latitude)`. Of course there should be unit tests in place to guarantee, that
  things work as expected, but it's still a bit of Jesus-driven-development, isn't it?
* [^4]: technically one could still mess it up the same as before when
  doing `PizzaName.fromString(pizzaDto.description())` but you got to be a special kind of stupid to mess that up and
  it's limited to the boundaries of our code
* [^5]: someone smarter than me has probably figured out a better name but that's what I call them ... (until I refactor
  the mess next week)
* [^6]: if we need it we can always add it.
* [^7]: every clean-code & clean-design & clean-architecture book ever written will tell you to not use the persistence
  layer from the controller-layer, yet that's exactly what I'm gonna do 😁

## Update

I'm obviously not the first one to come up with this "idea". Turns out DDD has a term for it which is less funky than
my 'Atomic-Property-Object' - they call it [Value Object](https://martinfowler.com/bliki/ValueObject.html), which
totally makes sense. I will adopt that naming from here on forward, but am still proud of my 'Atomic-Property-Objects' 😎.