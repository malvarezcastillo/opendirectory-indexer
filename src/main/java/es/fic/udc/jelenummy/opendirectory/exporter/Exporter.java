package es.fic.udc.jelenummy.opendirectory.exporter;

import java.io.FileInputStream;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.ArrayList;
import java.util.EnumSet;
import java.util.HashSet;
import java.util.List;
import java.util.Properties;
import java.util.Set;
import java.util.concurrent.ExecutionException;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.Future;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.TimeoutException;

import org.apache.http.client.methods.CloseableHttpResponse;
import org.apache.http.client.methods.HttpHead;
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
	private static String appId;
	private static String version;
	private static String redditUsername;
	private static String redditPassword;
	private static String redditClientId;
	private static String redditClientSecret;
	private static String outputFileName;
	private static Integer timeoutTime;

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
			HttpHead request = new HttpHead(url);

			CloseableHttpResponse response;
			request.addHeader("User-Agent",
					"Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36");
			response = httpClient.execute(request);
			return (response.getStatusLine().getStatusCode() >= 200 && response.getStatusLine().getStatusCode() <= 399);
		} catch (IOException e) {
			return false;
		}
	}

	private static void init(String rootPath) {
		String appConfigPath = rootPath + "exporter.properties";

		Properties p = new Properties();
		try (FileInputStream fs = new FileInputStream(appConfigPath)) {
			p.load(fs);
			appId = p.getProperty("reddit.appId", "es.fic.udc.jelenummy.opendirectory-indexer");
			version = p.getProperty("version");
			redditUsername = p.getProperty("reddit.username");
			redditPassword = p.getProperty("reddit.password");
			redditClientId = p.getProperty("reddit.redditClientId");
			redditClientSecret = p.getProperty("reddit.redditClientSecret");
			outputFileName = p.getProperty("outputFilename");
			timeoutTime = Integer.parseInt(p.getProperty("timeout"));

			if (version == null) {
				throw new MissingPropertyException("version");
			}
			if (redditUsername == null) {
				throw new MissingPropertyException("redditUsername");
			}
			if (redditPassword == null) {
				throw new MissingPropertyException("redditPassword");
			}
			if (redditClientId == null) {
				throw new MissingPropertyException("redditClientId");
			}
			if (redditClientSecret == null) {
				throw new MissingPropertyException("redditClientSecret");
			}
			if (outputFileName == null) {
				throw new MissingPropertyException("outputFileName");
			}
			if (timeoutTime == null) {
				throw new MissingPropertyException("timeoutTime");
			}

		} catch (NumberFormatException e) {
			logger.error("Incorrect numeric property {}", e);
			System.exit(-1);
		} catch (IOException e) {
			logger.error("Error opening properties file {}", e);
			System.exit(-1);
		} catch (MissingPropertyException e) {
			logger.error("Missing property {}", e);
			System.exit(-1);
		}

	}

	public static void main(String[] args) throws OAuthException {
		init(Thread.currentThread().getContextClassLoader().getResource("").getPath());
		// https://github.com/mattbdean/JRAW/wiki/Quickstart
		List<Submission> posts = new ArrayList<>();
		Set<String> urls = new HashSet<>();
		Set<String> availableUrls = new HashSet<>();

		UserAgent myUserAgent = UserAgent.of("desktop", appId, version, redditUsername);
		RedditClient redditClient = new RedditClient(myUserAgent);
		Credentials credentials = Credentials.script(redditUsername, redditPassword, redditClientId,
				redditClientSecret);

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

			Future<Boolean> future = executor.submit(() -> checkUrl(url));

			try {
				if (future.get(timeoutTime, TimeUnit.SECONDS)) {
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
		Path path = Paths.get(outputFileName);
		byte[] strToBytes = urlsString.getBytes();
		try {
			Files.write(path, strToBytes);
			logger.info("Wrote Available URLs to file");
		} catch (IOException e) {
			logger.error("Error while writing URLs to file {}", e);
		}

		System.exit(0);
	}
}
