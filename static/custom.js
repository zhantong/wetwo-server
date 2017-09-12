$(document).ready(function () {
    $('.btnReplyComment').click(function () {
        var form = $('#' + $(this).data('target-form'));
        form.find('div.input-group > input[name="parentCommentId"]').val($(this).data('commentid'));
        form.find('div.input-group > span.input-group-addon').text('回复 ' + $(this).data('userid'));
    });
    $('.formComment').submit(function () {
        $.ajax({
            method: 'POST',
            url: 'postComment',
            data: $(this).serialize()
        });
        return false;
    });
});