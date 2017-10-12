package es.fic.udc.jelenummy.opendirectory.exporter;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.ArrayList;
import java.util.EnumSet;
import java.util.HashSet;
import java.util.List;
import java.util.Set;
import java.util.concurrent.ExecutionException;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.Future;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.TimeoutException;

import org.apache.http.client.methods.CloseableHttpResponse;
import org.apache.http.client.methods.HttpGet;
import org.apache.http.impl.client.CloseableHttpClient;
import org.apache.http.impl.client.HttpClientBuilder;
import org.nibor.autolink.LinkExtractor;
import org.nibor.autolink.LinkSpan;
import org.nibor.autolink.LinkType;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import net.dean.jraw.RedditClient;
import net.dean.jraw.http.UserAgent;
import net.dean.jraw.http.oauth.Credentials;
import net.dean.jraw.http.oauth.OAuthData;
import net.dean.jraw.http.oauth.OAuthException;
import net.dean.jraw.models.Listing;
import net.dean.jraw.models.Submission;
import net.dean.jraw.paginators.SubredditPaginator;

public class Exporter {

	private static final Logger logger = LoggerFactory.getLogger(Exporter.class.getName());

	// https://github.com/robinst/autolink-java
	private static List<String> extractURLs(String input) {
		List<String> linksToReturn = new ArrayList<>();
		LinkExtractor linkExtractor = LinkExtractor.builder().linkTypes(EnumSet.of(LinkType.URL)).build();
		Iterable<LinkSpan> links = linkExtractor.extractLinks(input);
		for (LinkSpan link : links) {
			link.getBeginIndex();
			link.getEndIndex();
			linksToReturn.add(input.substring(link.getBeginIndex(), link.getEndIndex()));
		}
		return linksToReturn;
	}

	private static boolean checkUrl(String url) {
		try (CloseableHttpClient httpClient = HttpClientBuilder.create().disableAutomaticRetries().build()) {
			HttpGet httpGet = new HttpGet(url);

			CloseableHttpResponse response;
			httpGet.addHeader("User-Agent",
					"Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36");
			try {
				response = httpClient.execute(httpGet);
			} catch (IOException e) {
				return false;
			}
			return (response.getStatusLine().getStatusCode() >= 200 && response.getStatusLine().getStatusCode() <= 399);
		} catch (IOException e) {
			return false;
		}
	}

	public static void main(String[] args) throws OAuthException {
		// https://github.com/mattbdean/JRAW/wiki/Quickstart
		List<Submission> posts = new ArrayList<>();
		Set<String> urls = new HashSet<>();
		Set<String> availableUrls = new HashSet<>();

		UserAgent myUserAgent = UserAgent.of("desktop", "es.fic.udc.jelenummy.opendirectory.exporter", "0.0.1-SNAPSHOT",
				"opendirectoriesindex");
		RedditClient redditClient = new RedditClient(myUserAgent);
		Credentials credentials = Credentials.script("opendirectoriesindex", args[0], "S-cIDhMuFf1rDA",
				"5cCiiVRM_rSduPuZh8Qf5e_z-gE");

		OAuthData authData = redditClient.getOAuthHelper().easyAuth(credentials);
		redditClient.authenticate(authData);

		// https://github.com/mattbdean/JRAW/wiki/Paginators
		SubredditPaginator paginator = new SubredditPaginator(redditClient);
		paginator.setSubreddit("opendirectories");
		Listing<Submission> firstPage;

		while (paginator.hasNext()) {
			firstPage = paginator.next();
			for (Submission submission : firstPage) {
				posts.add(submission);
			}
		}

		logger.info("Got {} posts.", posts.size());

		for (int i = 0; i < posts.size(); i++) {
			Submission s = posts.get(i);
			if (s.isSelfPost()) {
				urls.addAll(extractURLs(s.getSelftext()));
			} else {
				urls.add(s.getUrl());
			}
		}
		logger.info("Got {} urls.", urls.size());
		int i = 0;
		for (String url : urls) {
			logger.info("Checking ({} of {}): {}", ++i, urls.size(), url);

			ExecutorService executor = Executors.newFixedThreadPool(1);

			Future<Boolean> future = executor.submit(() -> {
				return checkUrl(url);
			});

			try {
				if (future.get(15, TimeUnit.SECONDS)) {
					logger.info("URL {} is AVAILABLE", url);
					availableUrls.add(url);
				} else {
					logger.warn("URL {} is DOWN", url);
				}
			} catch (InterruptedException | ExecutionException | TimeoutException e) {
				logger.warn("URL {} is DOWN (Timed Out)", url);
			}

		}

		logger.info("Got {} available urls.", availableUrls.size());

		String urlsString = String.join("\n", availableUrls);
		Path path = Paths.get(args[1]);
		byte[] strToBytes = urlsString.getBytes();
		try {
			Files.write(path, strToBytes);
		} catch (IOException e) {
			logger.error("Error while writing URLs to file {}", e);
		}

	}

}
