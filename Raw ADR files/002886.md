# Use a WebView to load full article content
6 March 2025  
Status: Approved  
Author: Matthew Bryant

## Overview
This proposal seeks to clarify the design and high-level implementation of showing the full news article content by using a web view. In this context, an article's **content** refers to the text of the article.

## Background
The app data source is powered by [NewsAPI.org](https://newsapi.org/). According to their FAQs, the full article content is not available via API. Instead, the content text is limited by character count, thus making it impossible for a user to read the full article text.

In the current implementation, when tapping an article preview in the feed, the app loads a more full version of the content on screen. The content consists of:
- image — an image associated with the article
- title — the title of the article
- content — the article text, limited by character count, with remaining characters displayed at the end of the truncated text. For example, `...[+4152 chars]`
- source — the news agency responsible for the article, for example "BBC News"
- time - text which indicates how much time has passed since the story was published

## Goals
Enable the user to view the full content of the article where possible.

## Non-goals
Do not attempt to
- bypass article host paywalls
- pass cookies or introduce any cross-site tracking 
- track a user's activity on the host site

## Proposed solution
The API returns a URL that links to the host of the article source. For example, in the response object for an article from BBC News, the URL property might contain `https://www.bbc.com/news/article-title-in-url-form`. In cases where this URL is available, the article reader screen displays a button or link to view the full article content. 

### Additional UI improvements
- try to trim the not-so-nice-looking character count from the tail of the content text. For example, `[+4152 chars]`. If not possible to trim or if it makes sense to give the user an estimate of the remaining character count, the app should display it in a better format.


## Security concerns
The app should use a secure web view and app transit security to prevent man-in-the-middle attacks and session highjacking.

## Tradeoffs
It might be a better user experience to simply load the article into a web view immediately upon tapping the preview — thus bypassing the reader screen with the abbreviated content, and saving the user an additional tap. It's possible though that the article data may not have an URL. What should the app do in that case?

With the proposed solution, the fallback case is covered by simply not showing the link. It's possible that the above approach could be backed up by simply showing the reader screen.

Additionally, loading the article URL in a webview might not acheive the stated goal. Paywalls, and cookie tracking may either prevent or deter a user from reading the article on a host's site. Therefore, the goal should stay tightly focused on **enabling** the user to view the full article content, rather than **ensuring** that they view it.

## Decision
After POC exploration, the app will attempt to load the URL directly into the webview when the user taps the article preview. If the URL cannot be loaded, the app will display an error message and with a button close the webview and navigate back to the feed screen.