package es.fic.udc.jelenummy.opendirectory.exporter;

import java.util.ArrayList;
import java.util.EnumSet;
import java.util.HashSet;
import java.util.List;
import java.util.Set;

import org.nibor.autolink.LinkExtractor;
import org.nibor.autolink.LinkSpan;
import org.nibor.autolink.LinkType;

import net.dean.jraw.RedditClient;
import net.dean.jraw.http.NetworkException;
import net.dean.jraw.http.UserAgent;
import net.dean.jraw.http.oauth.Credentials;
import net.dean.jraw.http.oauth.OAuthData;
import net.dean.jraw.http.oauth.OAuthException;
import net.dean.jraw.models.Listing;
import net.dean.jraw.models.Submission;
import net.dean.jraw.paginators.SubredditPaginator;

public class Exporter {

	// https://github.com/robinst/autolink-java
	private static List<String> extractURLs(String input) {
		List<String> linksToReturn = new ArrayList<String>();
		LinkExtractor linkExtractor = LinkExtractor.builder().linkTypes(EnumSet.of(LinkType.URL)).build();
		Iterable<LinkSpan> links = linkExtractor.extractLinks(input);
		for (LinkSpan link : links) {
			link.getBeginIndex();
			link.getEndIndex();
			linksToReturn.add(input.substring(link.getBeginIndex(), link.getEndIndex()));
		}
		return linksToReturn;
	}

	public static void main(String[] args) throws NetworkException, OAuthException {
		// https://github.com/mattbdean/JRAW/wiki/Quickstart
		List<Submission> posts = new ArrayList<Submission>();
		Set<String> urls = new HashSet<String>();

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

		System.out.println("Got " + posts.size() + " posts!");

		for (int i = 0; i < posts.size(); i++) {
			Submission s = posts.get(i);
			if (s.isSelfPost()) {
				urls.addAll(extractURLs(s.getSelftext()));
			} else {
				urls.add(s.getUrl());
			}
		}

		System.out.println("Got " + urls.size() + " urls!");

	}

	/*
	 * Getting by timestamps... SubmissionSearchPaginator p = new
	 * https://github.com/mattbdean/JRAW/issues/100
	 * SubmissionSearchPaginator(redditClient, "timestamp:1420070400..1421020800");
	 * p.setSubreddit("opendirectories"); p.setLimit(1000);
	 * 
	 * p.setSyntax(SubmissionSearchPaginator.SearchSyntax.CLOUDSEARCH);
	 * Listing<Submission> submissions = p.next();
	 */
}
