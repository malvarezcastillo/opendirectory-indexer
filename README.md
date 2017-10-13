# opendirectory-indexer
Indexes open directories from /r/opendirectories/

Compile with: mvn -s settings.xml clean compile assembly:single

Change exporter.properties.example and copy to exporter.properties using your reddit info

Run with: java -jar target/opendirectory-indexer-0.0.2-jar-with-dependencies.jar exporter.properties

Web crawling using: http://nutch.apache.org/
Indexing and search using: http://lucene.apache.org/solr/features.html
