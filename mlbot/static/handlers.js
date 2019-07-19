define(['jquery', 'base/js/namespace', 'base/js/dialog'], function($, Jupyter, dialog) {
    "use strict";
    // use get request to call api endpoint(written in python tornado) 
    // which copies over the selected version
    var select_version_handler = function () {  
        var selected_version = $("select#version_picker").find(":selected");
        var base_url = window.location.origin;
        var post_url = base_url + '/selectversion';
        
        if (selected_version.attr("fpath") != 'header') {
            $.ajax({
                type: 'GET',
                url: post_url,
                data: { fpath: selected_version.attr("fpath") },
                dataType: "text",
                success: function (response) {
                    console.log('Successfully changed notebook version');
                    window.location.reload();
                }
            });
        }
    };

    var alert_handler = function () {
        alert('Coming soon!')
    };

    var save_version_locally_handler = function (env) {
        Jupyter.notebook.save_checkpoint();
        var p = $('<p/>').text("Notes for this version. It'll be displayed when hover over a version in the dropdown menu.")
        var input = $('<textarea rows="4" cols="72"></textarea>')
        var div = $('<div/>')

        div.append(p)
            .append(input)
        
        function on_click_ok() {
            var base_url = window.location.origin;
            // eg. /notebooks/test.ipynb  rm /notebooks/ later
            var fpath = window.location.pathname;
            var post_url = base_url + '/savelocally';

            $.ajax({
                type: "GET",
                url: post_url,
                data: {
                    fpath : fpath,
                    note : input.val()
                },
                dataType:"text",
                success: function (response) {
                    window.location.reload();
                    console.log('Successfully saved notebook version')
                },
                error: function (response) {
                    console.log('Error occured')
                }
            });
        };

        dialog.modal({
            body: div,
            title: 'Save notebook locally',
            buttons: {
                'Save locally':
                {
                    class: 'btn-primary btn-large',
                    click: on_click_ok
                },
                'Cancel': {}
            },
            notebook: env.notebook,
            keyboard_manager: env.notebook.keyboard_manager
        });
    };
    
    var save_version_to_github_handler = function (env) {
        var on_success = undefined;
        var on_error = undefined;
        var p = $('<p/>').text("Please enter your commit message. Only this notebook will be committed.")
        var input = $('<textarea rows="4" cols="72"></textarea>')
        var div = $('<div/>')
        div.append(p)
            .append(input)
        
        // get the canvas for user feedback
        var container = $('#notebook-container');

        function on_ok() {
            Jupyter.notebook.save_checkpoint();
            var re = /^\/notebooks(.*?)$/;
            var filepath = window.location.pathname.match(re)[1];
            var payload = {
                'fpath': filepath,
                'note': input.val()
            };
            var settings = {
                url: '/git/commit',
                processData: false,
                type: "PUT",
                dataType: "json",
                data: JSON.stringify(payload),
                contentType: 'application/json',
                success: function (data) {

                    // display feedback to user
                    var container = $('#notebook-container');
                    var feedback = '<div class="commit-feedback alert alert-success alert-dismissible" role="alert"> \
                                    <button type="button" class="close" data-dismiss="alert" aria-label="Close"><span aria-hidden="true">&times;</span></button> \
                                    '+ data.statusText + ' \
                                    \
                                </div>';

                    // display feedback
                    $('.commit-feedback').remove();
                    container.prepend(feedback);
                },
                error: function (data) {

                    // display feedback to user
                    var feedback = '<div class="commit-feedback alert alert-danger alert-dismissible" role="alert"> \
                                    <button type="button" class="close" data-dismiss="alert" aria-label="Close"><span aria-hidden="true">&times;</span></button> \
                                    <strong>Warning!</strong> Something went wrong. \
                                    <div>'+ data.statusText + '</div> \
                                </div>';

                    // display feedback
                    $('.commit-feedback').remove();
                    container.prepend(feedback);
                }
            };

            // display preloader during commit and push
            var preloader = '<img class="commit-feedback" src="https://cdnjs.cloudflare.com/ajax/libs/slick-carousel/1.5.8/ajax-loader.gif">';
            container.prepend(preloader);

            // commit and push
            $.ajax(settings);
        };

        dialog.modal({
            body: div,
            title: 'Commit and Push Notebook',
            buttons: {
                'Commit and Push':
                {
                    class: 'btn-primary btn-large',
                    click: on_ok
                },
                'Cancel': {}
            },
            notebook: env.notebook,
            keyboard_manager: env.notebook.keyboard_manager
        });
    };


    return {
        save_version_locally_handler:save_version_locally_handler, 
        select_version_handler: select_version_handler, 
        alert_handler: alert_handler, 
        save_version_to_github_handler:save_version_to_github_handler
    };
});