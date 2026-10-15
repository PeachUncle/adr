# 11. Preload Translations in the Web Widget

Date: 2020-04-02

## Attendees

- Wayne See
- Lucas Hills
- Briana Coppard
- David Allen
- Daniel Bradford
- Kari Matthews
- Alex Robinson
- Levi Serebryanski
- Tim Patullock
- Adrian Yong
- Apoorv Kansal

## Status

Pending

## Results

Performance:
https://docs.google.com/spreadsheets/d/1eu0PiLI7osKXQjMgXhkDAQu5K_Bd873VO6AjCvLd87Y/edit?usp=sharing

Network Trace:
https://docs.google.com/document/d/1FgVQ1j14I1FSg-EFmqXGOtWMTi4U7dQQGL6coDj5XII/edit?usp=sharing

## Context

At the moment, the Web Widget uses [`client-i18n-tools`](https://github.com/zendesk/client-i18n-tools) to manage translations. In particular, it will load translations for a particular locale (locale returned from `/embeddable/config`) at the very end of the boot sequence. This results in the Web Widget waiting for the translations to be downloaded before showing the launcher pill which leads to an increase in response time. The ideal solution is to preload the translations in the `preload.js` file where it woulld download in parallel to the Web Widget asset. By the time the Web Widget sets the locale (at the end of the boot sequence), the translations will be locally available.

## Possible Approaches

### 1. Remove `client-i18n-tools` and manage translations independently

POC: https://github.com/zendesk/embeddable_framework/pull/3730

The Web Widget is heavily coupled with the `client-i18n-tools` making it harder to preload the translations. A solution can be to remove this package and work on our implementation to manage translations. We can remove the `client-i18n-tools` dependency completely and manage translations within the Web Widget.

#### Pros

##### Managed by us

We have full autonomy on how and when translations will be deployed, downloaded and accessed. This gives more visibility and transparency on how translations are managed in the Web Widget which opens up opportunities for further optimizations and creative solutions.

##### Reduces response time

The widget will no longer render block to fetch translations so we will see some performance improvements.

#### Cons

##### Increases bundle size

The solution increases the preload bundle from 59.11 KB to 65.83 KB. We will need to bundle extra code into `preload.js` so it can fetch the translations correctly. This includes accessing and formatting the browser API locale. However, the web widget package size decreases from 2240 KB to 2160 KB as a result of removing the `client-i18n-tools` package.

##### Increases Complexity

The POC has shown that it is much more complex to deploy and fetch translations. We will need to reimplement a lot of work managed by `client-i18n-tools`.

### 2. Bundle `client-i18n-tools` into `preload.js`

POC: https://github.com/zendesk/embeddable_framework/pull/3766

We can just bundle the package into `preload.js` and fetch translation at that point.

#### Pros

##### Simplest Solution

This implementation is fairly easy to implement with the least number of risks associated.

##### Reduces response time

The widget will no longer render block to fetch translations so we will see some performance improvements.

#### Cons

##### Increases bundle size

The solution increases preload bundle from 59.11 KB to 74.42 KB because we need to bundle a full blown package into `prelod.js`.

##### Blackbox deployment sequence

It complicates our deployment sequence. We need to download the translation JSON files and metadata and then their Webpack plugin take these json files and output JS files that simply inject the translations onto the window.i18n. Although the new solution still downloads the JSON files and metadata, it is a lot simpler to understand and the logic is much more visible and transparent. Currently, the i18n tools package abstracts this logic which makes it harder to optimise the deploy sequence in future.

##### Locale state

`client-i18n-tools` maintains its own state of the current locale which needs to be synchronised with the WW locale state. Every time we update the locale, we will need to update the locale in `client-i18n-tools`.

##### Slow deployment

`client-i18n-tools` sequentially downloads each translation which is slow. With the new implementation, we can make X numbers of translation file requests in parallel and thereby decrease the deploy sequence time. Note that we need to decide an appropriate number of requests to make in parallel that will not flood Rosetta.

### 3. Download translations early but store them into `client-i18n-tools` when ready

POC: https://github.com/zendesk/embeddable_framework/pull/3765

We can download the translations in `preload.js` and then use the api provided by `client-i18n-tools` to set the translations when we have downloaded the Web Widget.

#### Pros

##### Simplest Solution

This implementation is fairly easy to implement with a few number of risks associated with the deployment sequence. For example, don't need to use the `i18nPlugin` to compile raw translation files.

##### Consistency with other teams

We will maintain the same implementation as other teams. This means that developers from other teams can easily understand how we use translations if they need to access our codebase.

##### Best Performance

Based on the results, this solution has the lowest response time and also manages the package size across all assets fairly well.

#### Cons

##### Developers required to have a better understanding of Webpack and Dynamic Imports

This requires developers to have a better understanding of Webpack.

### 4. Don't do anything

#### Pros

##### Consistency with other teams

We will maintain the same implementation as other teams. This means that developers from other teams can easily understand how we use translations if they need to access our codebase.

#### Cons

##### No Performance Improvements

We will still see the widget render block until the translations have been downloaded.

## Decision

Selected Approach 3.
