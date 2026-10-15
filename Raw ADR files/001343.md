# Feature sets for banner tests

- Status: accepted
- Deciders:
	- Gabriel Birke <gabriel.birke@wikimedia.de>
	- tado
- Date: 2022-12-15

## Context

When testing banners, we want to test individual "features" or
"requirements" of banners. To avoid specifying long command lines where
you have to name all the features, we need a way to collect features into "feature sets".

All features share the interface: a method call `runSteps` that gets
passed a `Banner` instance.


```javascript
// Example feature test class
export default class BannerClosesOnClick {
	runSteps(banner) {
		banner.waitForBannerToShow()
			.clickOnCloseButton()
			.checkThatBannerIsInvisble()
	}
}
```

This document is about figuring out an API and command line shape mof
collecting together the individual features into a named set.


## Decision Drivers

- The command line should be as short and reusable as possible, ideally
	one feature set name plus banner name
- For consistency reasons, we should only start one browser instance and
	run the feature tests sequentially. In the future, we *may* run them
	in parallel, but this would need a queueing mechanism.
- We want to re-use the feature sets as much as possible across banners.
- We want to accommodate for new banners with new features or changed
	behavior. We'll probably rather duplicate feature sets than make them "composable",
	to keep the command line short.
- We want to avoid repetition as much as possible. Adding a new feature
	should have as few changes in other files as possible.
- The command line might be run be non-developers who are technically
	competent but don't want to browse though code files.

### Use cases
- Run a test to find out if a banner is correct.
	- Figure out *which* feature set to use for a banner
	- Figure out how two feature sets differ from each other 
- Add a new feature test. Add it to *some* of the existing feature sets or
	create a new one.
- Create a new feature set
	- Figure out *which* features to switch out
	- Write a new feature test (or copy and modify and existing one) and include it in existing sets
- Fix a failing feature test (when the code is wrong but not the banner)
 
Our gut feeling is that after the initial creation of all the feature
tests we'll probably write new feature sets and add 90% of the existing
tests to them and one or two new feature tests.

## Considered options

### 0. No grouping, specify each feature

	npm run dandy -- -b B22_WMDE_Test_07 close_works form_validates \
		banner_slides_in

#### Cons
- Long command lines
- Multiple browser instances

#### Pro
Status quo, no changes needed

### 1. JavaScript files with imports

	npm run dandy -- -b B22_WMDE_Test_07 base_features
	npm run dandy -- -b B22_WMDE_Test_07 mobile_banner


In a test file like `base_features` we'd have code like

```javascript
import BannerSlidesIn from './features/banner_slides_in'
import BannerClosesOnClick from './features/banner_closes'
import SliderStopsOnInteraction from './features/banner_slider_stops_on_interaction'

const banner = new Banner( /* some params */)
const featureSet = new FeatureSet(
	'Base features',
	[
		BannerSlidesIn,
		BannerClosesOnClick,
		SliderStopsOnInteraction
	]
)

await featureSet.runTests(banner);

```

#### Con
Adding a new feature means editing 2 lines in all the files that use this
feature, adding an `import` statement and adding the class name to the `FeatureSet` constructor.

#### Pro:
No change to existing dandy CLI

### 3. "sets" property in features 

Feature classes have a "sets" property that specify the sets that they belong to

```javascript

class BannerClosesOnClick {
	sets: [
		'base_features',
		'mobile_banner'
	],
	runSteps( banner ) {
		// ...
	}
}
```

#### Cons
- Adding a new feature set means editing the `sets` property of *all*
	features that support it.
- Small performance impact of importing all the feature files instead of
	dynamically importing

#### Pro
New features don't need changes in other files, only new feature sets.


### 3. Configuration file

	npm run dandy -- -b B22_WMDE_Test_07 base_features

We have a YAML configuration file that lists which feature tests belong to which
set

```YAML
base_features:
	description: "Features that all banners must support"
	features:
		- banner_slides_in
		- banner_closes
		- banner_slider_stops_on_interaction

mobile_banner:
	description: "All tests for a mobile banner"
	features:
		- banner_slides_in
		- banner_closes
		- banner_slider_stops_on_interaction
		- form_slides_in_on_click

```

We choose YAML over JSON because
1. There is fewer "boilerplate" (quoted strings, array brackets, etc)
2. We can comment out individual features in a set while developing/bugfixing (JSON doesn't support comments)
3. Hierarchical structure more easy to read

### Cons
- Not so easy to peek into the feature tests (jumping around in the
  IDE), renaming files means also renaming things in YAML.
- feature sets are less easy to compare when they are in one file (as
	opposed to solution 1 where you can run a `diff` command to compare
	feature sets)
- Performance impact when parsing config (is negligible)
- Adding new a feature means adding a new line to all feature sets that use this
  feature

### Pros
- More user friendly (readable)
- More compact
- Creating new feature sets with copy-paste is super fast

## Decision outcome

We will go with the YAML configuration file because it best supports our
decision drivers and use cases.



