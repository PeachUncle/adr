# 2: Storage Engines 

Date: 2018-05-28

## Status

Proposed

## Context

Context goes here. Describe the forces at play, including technological, political, social, and project local. 
These forces are likely in tension, and should be called out as such. The language in this section is value-neutral. It is simply describing facts. Rationale should be self-evident from the context


I dont have the necessary expertise to make a custom storage engine, like EventStore, and even if I did I still don't think it would make sense to try and build a custom storage engine. Building a storage engine is not a trivial task and are some of the hardest and most important parts of a database (kelly sommers). A database is all about it's storage engine(s) (Kelly Sommers). Instead I think it makes sense to leverage an exisitng storage engine.

We should have a pluggable storage engine system


## Decision
This section describes our response to these forces. It is stated in full sentences,
with active voice. "We will ...“


RocksDB - LSM
LMDB - B+ Tree
WiredTiger - offers both B+ Tree and LSM

https://github.com/wiredtiger/wiredtiger/wiki/Btree-vs-LSM
https://yahooeng.tumblr.com/post/104861108931/mdbm-high-speed-database
http://www.lmdb.tech/bench/inmem/
http://smalldatum.blogspot.com/2016/01/summary-of-advantages-of-lsm-vs-b-tree.html
http://smalldatum.blogspot.com/2015/11/read-write-space-amplification-b-tree.html
https://medium.com/databasss/on-disk-io-part-3-lsm-trees-8b2da218496f
https://www.percona.com/live/17/sites/default/files/slides/Heaps%20B-trees%20log%20structured%20merge%20trees%202017-04-25.pptx_.pdf
http://akumuli.org/akumuli/2017/08/01/storage-engine-design2/




WiredTiger require building it ourselves / not on maven
central/repository and based we can cover both LSM and B+ Tree with
RocksDB and LMBD.


## Consequences

This section describes the resulting context, after applying the decision. All consequences should be listed here, not just the "positive" ones. A particular decision may have positive, negative, and neutral consequences, but all of them affect the team and project in the future.


The whole document should be one or two pages long. We will write each ADR as if it is a conversation with a future developer. This requires good writing style, with full sentences organized into paragraphs. Bullets are acceptable only for visual style, not as an excuse for writing sentence fragments. (Bullets kill people, even PowerPoint bullets.)

