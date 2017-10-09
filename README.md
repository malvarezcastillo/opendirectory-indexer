# opendirectory-indexer
Indexes open directories from /r/opendirectories/

Compile with: mvn -s settings.xml clean compile assembly:single

Run with: java -jar target/opendirectory-indexer-{VERSION}-jar-with-dependencies.jar {REDDIT_PASSWORD}

Web crawling using: http://nutch.apache.org/
Indexing and search using: http://lucene.apache.org/solr/features.html
