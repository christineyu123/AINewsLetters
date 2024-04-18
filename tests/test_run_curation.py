from article_curation.run_curation import get_user_query_results


def test_get_user_query():
    results = get_user_query_results()
    assert len(results) > 0
    for query, destination in results:
        assert query is not None
        assert destination is not None
 