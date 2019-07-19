define(['jquery', 'base/js/namespace', 'base/js/dialog', './handlers'], function($, Jupyter, dialog, handlers) {
    "use strict";

    // build UI elements and add them to toolbar
    var build_ui = function () {
        // dropdown menu for version selection
        var dropdown = $("<select></select>").attr("id", "version_picker")
            .css("margin-left", "0.75em")
            .attr("class", "form-control select-xs")
            .change(handlers.select_version_handler);
        
        // buttons for version saving
        var prefix = 'snapbot';
        var save_locally = {
            icon: 'fa-history',
            help: 'Save version locally',
            help_index: '',
            handler: handlers.save_version_locally_handler
        };
        var save_github = {
            icon: 'fa-github',
            help: 'Commit to github',
            help_index: '',
            handler: handlers.save_version_to_github_handler
        };
        var save_gitlab = {
            icon: 'fa-gitlab',
            help: 'Commit to gitlab',
            help_index: '',
            handler: handlers.alert_handler
        };
        var save_locally_action = Jupyter.actions.register(save_locally, 'save_locally', prefix);
        var save_github_action = Jupyter.actions.register(save_github, 'save_github', prefix);
        var save_gitlab_action = Jupyter.actions.register(save_gitlab, 'save_gitlab', prefix);
        Jupyter.toolbar.element.append(dropdown);
        Jupyter.toolbar.add_buttons_group([save_locally_action, save_github_action, save_gitlab_action]);

        // index versions for dropdown menu
        var option = $("<option></option>")
            .attr("id", "menu_header")
            .text("Versions");
        $("select#version_picker").append(option);
        
        var url = window.location.pathname;
        var fname = url.substring(url.lastIndexOf('/')+1);
        var fname_only = fname.substring(0,fname.indexOf('.'))
            
        $.getJSON("./nb_versions/"+fname_only+"/version_log.json", function(data) {
            $.each(data['versions'], function(key, version) {
                var option = $("<option></option>")
                    .attr("fpath", version['fpath'])
                    .text('v' + version['version'].toString())
                    .prop('title', version['note']);
                $("select#version_picker").append(option);
            });
        })
        .error(function(jqXHR, textStatus, errorThrown) {
            // Add an error message if the JSON fails to load
            var option = $("<option></option>")
                         .attr("value", 'ERROR')
                         .text('Error: failed to load snippets!')
                         .attr("code", "");
            $("select#version_picker").append(option);
        });
    };
    
    // will be called when the nbextension is loaded
    function load_extension() {
        build_ui();
    };    

    // return public methods
    return {
        load_ipython_extension : load_extension
    };
});