# ADR-0002 Extrernal API Integration

Status: Rejected <br>
Date: 2023-05-10 <br>
Deciders: Andrew Onozuka, Merrick Qiu, Abhimanyu Srivastava, Yuantian Zhou <br>
Consulted: Professor Thomas A. Powell, Malcolm McSwain (TA) <br>
Informed: Alex Tahan, Joseph Del Val, Vivin Vinil, Julia Poon, Jacob Felts, Leo Lee

## Context and Problem Statement

We rejected the use of external API's in order to operate our CRUD app, after speaking with Prof. Powell and our TA Malcolm, since we do not want our app to be reliant on services from external providers. Our goal now is to still be able to provide variable responses and specifically catered responses to unique inputs.

<!-- This is an optional element. Feel free to remove. -->
## Decision Drivers

* Reliance on external providers: relying on external sources to calculate horoscope results can produce conflicting results & things we do not want to include in our final app. 
* Unnecessary complications: we want to keep our app functional, but simple; using external sources to produce results can overcomplicate the process and overcomplicate parts of our project unnecessarily.

## Considered Options

* Using external sources to do all horoscope calculations and features
* Locally calculating horoscopes and implementing the calculations and features by hand

## Decision Outcome

Chosen option: "Locally calculating horoscopes", because while externally sourcing horoscope calculations can make use of more sofisticated calculation systems already in place, doing so locally serves our purpose better of "keeping things simple." It is also not too difficult to set calculations since our horoscope app will rely on the simplest way to calculate horoscopes, based purely on date of birth. 

<!-- This is an optional element. Feel free to remove. -->

## Pros and Cons of the Options

### Externally calculating horoscopes

<!-- This is an optional element. Feel free to remove. -->
* Good, because can save time doing calculations by hand
* Good, because it can give more sophisticated responses based on existing horoscope calculation databases
<!-- use "neutral" if the given argument weights neither for good nor bad -->
* Bad, because can unnecessarily overcomplicate the process
* Bad, because it can be difficult incorporating it into our own code
* Bad, because we can not tailor the calculations to fit our own purposes.

### Locally calculating horoscopes
* Good, because can tailor it to fit the purposes of our app perfectly
* Good, because we are able to control all aspects of the calculations and keep things simple
* Bad, because it can be time-consuming to calculate by hand

<!-- This is an optional element. Feel free to remove. -->
## More Information

Traditionally, horoscopes take a variety of information based not only on date of birth, but time and location of birth as well. If our app aimed to implement all those aspects, it may be more optimal to use external calculations as doing those can be tedious by hand. However, since our horoscope app will be simple in scope, taking into account only date of birth, it makes more sense to do the calculations by hand since it won't take that much extra time and we can customize the calculations more to fit our purposes and needs.
