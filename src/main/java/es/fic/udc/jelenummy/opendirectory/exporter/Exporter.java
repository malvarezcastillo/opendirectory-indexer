package es.fic.udc.jelenummy.opendirectory.exporter;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.ArrayList;
import java.util.EnumSet;
import java.util.HashSet;
import java.util.List;
import java.util.Random;
import java.util.Set;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.TimeUnit;

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

	private static final Logger logger = LoggerFactory.getLogger(Exporter.class);
	private static Set<String> availableUrls;

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

	public static void main(String[] args) throws OAuthException {
		// https://github.com/mattbdean/JRAW/wiki/Quickstart
		List<Submission> posts = new ArrayList<>();
		Set<String> urls = new HashSet<>();
		availableUrls = new HashSet<>();

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
		String urlsString = String.join("\n", urls);
		logger.info("Got {} urls.", urls.size());

		ExecutorService executor = Executors.newFixedThreadPool(urls.size());

		for (String url : urls) {
			executor.execute(new URLChecker(url));
		}

		executor.shutdown();
		try {
			if (!executor.awaitTermination(30, TimeUnit.SECONDS)) {
				executor.shutdownNow();
			}
		} catch (InterruptedException e) {
			executor.shutdownNow();
			Thread.currentThread().interrupt();
		}

		logger.info("Got {} available urls.", availableUrls.size());

		Path path = Paths.get(args[1]);
		byte[] strToBytes = urlsString.getBytes();
		try {
			Files.write(path, strToBytes);
		} catch (IOException e) {
			logger.error("Error while writing URLs to file {}", e);
		}

	}

	private static class URLChecker implements Runnable {
		private String url;

		private static boolean checkUrl(String url) {
			Random random = new Random();
			return random.nextBoolean();
		}

		public URLChecker(String url) {
			this.url = url;
		}

		@Override
		public void run() {
			if (checkUrl(url)) {
				availableUrls.add(url);
			}
		}
	}

}
