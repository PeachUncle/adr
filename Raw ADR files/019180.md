## Title
Default private setters on model

## Status
Draft

## Context
Our model consists of mutable JpaEntities on the one hand and immutable embeddable objects on the other.

The JpaEntities need to be mutable but the way to mutate them should not be by exposing setters for all fields.
Instead, we need to expose business methods which validate the input and change one or more fields at once.

Standard public setters for each field would inevitably cause our entities to become anemic, meaningless data containers.

Private chainable setter methods can be quite useful however.

Consider the following example, having fluent accessors (privately) allows easier chaining. 
```java
@Setter(AccessLevel.PRIVATE)
class A {
	private String remark;
	private Integer count;
	
	public A incrementCount() {
      if (count+1 > 100) {
        throw new IllegalArgumentException("Not allowed to count so high!");
      }
      count++;
	  return commentOnCount();
    }
	
    public A decrementCount() {
      if (count-1 < 0) {
        throw new IllegalArgumentException("Below 0 is not allowed!");
      }
      count--;
      return commentOnCount();
    }
	
    private A commentOnCount() {
      if (count > 10) {
        return remark(count + " is too much, I'll need to contact some friends...");
      } else if (count > 5) {
        return remark(count + " is too much for one hand man, good thing I have a second!");
      } else if (count > 0) {
        return remark(count + " is easy peasy, I can do this with just one hand!");
      } else {
        return remark("This is so easy I can do this in my sleep, hands down!");
      }
    }
	
    public A resetCount() {
      return count(0).remark("Recently Reset, I got nothing to show!");
    }
}

@Setter
class B {
  private String remark;
  private Integer count;
  // since setters are available, some incrementCount/decrementCount usecase can implement and the domain stays shallow,
}
```

## Decision
We will use lombok @Setter(AccessLevel.PRIVATE) on JpaEntities, not exposing setters by default, 
but allowing chainable fluent setting from within the entity.
When we wish to expose a setter explicitly, then just add it manually and increase its visibility.

## Compliance
An ArchUnit test checks @Setter is only used with AccessLevel.PRIVATE on JpaEntities.

## Notes
- Author: Gert Wijns
- Changelog:
    - 0.1 initial proposed version on 2025-01-12
