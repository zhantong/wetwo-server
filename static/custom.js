$(document).ready(function () {
    $('.btnReplyComment').click(function () {
        var form = $(this).closest('ul').next('form');
        form.find('div.input-group > input[name="parentCommentId"]').val($(this).data('commentid'));
        form.find('div.input-group > span.input-group-addon').text('回复 ' + $(this).data('userid'));
    });
    $('body').on('submit', '.formComment', function () {
        var formDom = $(this).closest('div.collapse');
        $.ajax({
            method: 'POST',
            url: 'postComment',
            cache: false,
            data: $(this).serialize()
        }).done(function (html) {
            formDom.html(html);
        });
        return false;
    });
});