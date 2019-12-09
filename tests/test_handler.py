# TODO: Write tests here.


class TestItemsApp(object):

    @patch.object(app, 'get_handler')
    def test_lambda_handler_get(self, mock_handler):
        event = {'httpMethod': 'GET'}
        app.lambda_handler(event, None)
        assert mock_handler.call_count == 1

    @patch.object(app, 'post_handler')
    def test_lambda_handler_post(self, mock_handler):
        event = {'httpMethod': 'POST'}
        app.lambda_handler(event, None)
        assert mock_handler.call_count == 1