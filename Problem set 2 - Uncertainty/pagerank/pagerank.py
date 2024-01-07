import os
import random
import re
import sys

DAMPING = 0.85
SAMPLES = 10000


def main():
    if len(sys.argv) != 2:
        sys.exit("Usage: python pagerank.py corpus")
    corpus = crawl(sys.argv[1])
    ranks = sample_pagerank(corpus, DAMPING, SAMPLES)
    print(f"PageRank Results from Sampling (n = {SAMPLES})")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")
    ranks = iterate_pagerank(corpus, DAMPING)
    print(f"PageRank Results from Iteration")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")


def crawl(directory):
    """
    Parse a directory of HTML pages and check for links to other pages.
    Return a dictionary where each key is a page, and values are
    a list of all other pages in the corpus that are linked to by the page.
    """
    pages = dict()

    # Extract all links from HTML files
    for filename in os.listdir(directory):
        if not filename.endswith(".html"):
            continue
        with open(os.path.join(directory, filename)) as f:
            contents = f.read()
            links = re.findall(r"<a\s+(?:[^>]*?)href=\"([^\"]*)\"", contents)
            pages[filename] = set(links) - {filename}

    # Only include links to other pages in the corpus
    for filename in pages:
        pages[filename] = set(
            link for link in pages[filename]
            if link in pages
        )

    return pages


def transition_model(corpus, page, damping_factor):
    """
    Return a probability distribution over which page to visit next,
    given a current page.

    With probability `damping_factor`, choose a link at random
    linked to by `page`. With probability `1 - damping_factor`, choose
    a link at random chosen from all pages in the corpus.
    """

    prob_dist = {}

    # Sets up the probability that any page is randomly selected from corpus
    page_links = corpus[page]
    if len(page_links) == 0:
        any_page_chance = 1 / len(corpus)
    else:
        any_page_chance = (1 - damping_factor) / len(corpus)
    for page_name in corpus:
        prob_dist[page_name] = any_page_chance

    # Sets up probability that one of the links is selected
    if len(page_links) != 0:
        page_link_chance = damping_factor / len(page_links)
        for link in page_links:
            prob_dist[link] += page_link_chance

    return prob_dist


def sample_pagerank(corpus, damping_factor, n):
    """
    Return PageRank values for each page by sampling `n` pages
    according to transition model, starting with a page at random.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """

    # Creates the pagerank dictionary using the corpus
    pagerank = {}
    for page_name in corpus:
        pagerank[page_name] = 0

    # Randomly selects a starting page before adding it to pagerank
    start_index = random.randint(0, len(pagerank) - 1)
    for index, page in enumerate(pagerank):
        if index == start_index:
            sample_page = page

    pagerank[sample_page] += 1

    # Using the initial starting page, runs through n iterations of sampling
    for i in range(n - 1):
        sample_dist = transition_model(corpus, sample_page, damping_factor)
        random_no = random.random()

        # Goes through probability distribution and adds probabilities until random number is exceeded
        probability_total = 0
        for page in sample_dist:
            probability_total += sample_dist[page]
            if probability_total >= random_no:
                sample_page = page
                break

        pagerank[sample_page] += 1

    # Normalises the pagerank probabilities
    for page in pagerank:
        pagerank[page] = pagerank[page] / n

    return pagerank


def iterate_pagerank(corpus, damping_factor):
    """
    Return PageRank values for each page by iteratively updating
    PageRank values until convergence.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """

    # Initialises the pagerank values
    pagerank = {}
    initial_rank = 1 / len(corpus)
    for page in corpus:
        pagerank[page] = initial_rank
        
        if len(corpus[page]) == 0:
            for add_link in corpus:
                corpus[page].add(add_link)

    max_change = 1
    pagerank_const = (1 - damping_factor) / len(corpus)

    while max_change > 0.001:
        max_change = 0

        # Iterates through all pages to change pagerank
        for page_p in corpus:

            # Finds pages which link to page p and finds probability of clicking p link
            link_prob = 0
            for page_i in corpus:
                if page_p in corpus[page_i]:
                    link_no = len(corpus[page_i])
                    link_prob += pagerank[page_i] / link_no


            # Finds the new pagerank probability
            new_rank = pagerank_const + damping_factor * (link_prob)
            
            # Finds the difference between old and new rank
            rank_change = abs(new_rank - pagerank[page_p])
            if rank_change > max_change:
                max_change = rank_change

            pagerank[page_p] = new_rank

    return pagerank


if __name__ == "__main__":
    main()
