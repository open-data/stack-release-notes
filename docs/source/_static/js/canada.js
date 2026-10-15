window.addEventListener('load', function(){

  $(document).ready(function(){

    // URL Params
    const urlParams = new URLSearchParams(window.location.search);
    // END URL Params END


    // GitFlow Diagram
    const diagram_container = document.getElementById('gitflow-diagram');
    const gitflow = `
      ---
        config:
            gitGraph:
                titleTopMargin: 50
                diagramPadding: 0
            theme: default
            themeVariables:
                git0: '#284162'
                gitInv0: '#ffffff'
                gitBranchLabel0: '#ffffff'
                git1: '#bc3331'
                gitInv1: '#bc3331'
                gitBranchLabel1: '#ffffff'
                git2: '#2572b4'
                gitInv2: '#2572b4'
                gitBranchLabel2: '#ffffff'
                git3: '#008888'
                gitInv3: '#008888'
                gitBranchLabel3: '#ffffff'
                git4: '#622841'
                gitInv4: '#622841'
                gitBranchLabel4: '#ffffff'
                git5: '#492862'
                gitInv5: '#492862'
                gitBranchLabel5: '#ffffff'
      ---
      gitGraph
          commit id: "INIT"
          branch "hotfix/*"
          commit id: "Critical Fixes" type: HIGHLIGHT
          checkout main
          branch release
          commit id: "Start New Release"
          branch "feature/*"
          commit id: "Code Changes" type: HIGHLIGHT
          checkout main
          merge "hotfix/*" tag: "release/YYYY.MM.DD.hotfix"
          checkout release
          commit id: " " type: NORMAL
          merge "feature/*"
          checkout main
          merge release tag: "release/YYYY.MM.DD"
          checkout release
          branch "staging"
          commit id: "Hanging Env (Staging)"
          checkout release
          branch "dev"
          commit id: "Hanging Env (Test)"
    `;
    mermaid.initialize({
      startOnLoad: false,
      securityLevel: 'strict',
      useMaxWidth: true,
    });
    let createdDiagram = false;
    document.querySelectorAll('details').forEach(_details => {
      _details.addEventListener('toggle', () => {
        if( createdDiagram ){
          return;
        }
        if( _details.open ){
          createdDiagram = true;
          const diagram = document.createElement('div');
          diagram.className = 'mermaid';
          diagram.textContent = gitflow;
          diagram_container.appendChild(diagram);
          mermaid.run({
            nodes: [diagram]
          }).catch(_err => {
            console.error('Unable to render Mermaid diagram: ', _err);
            createdDiagram = false;
            diagram_container.textContent = '';  // hide front-end error
          });
        }
      });
    });
    // END GitFlow Diagram END


    // Pre Release Functionality
    const t = 'WjJsMGFIVmlYM0JoZEY4eE1VRllSalpGVEVrd1pVYzFXakpoUVVkR2NuZDNYMFZyTTA0ME9FNVNZV0ZqU3pkaFNrTXpVR1EyYkhoR2IyVkpjbkpwTmtGS1FubDRlRUpWU1RsTmNVNUpSVTR5UWpaV1JUSkhWakZqWVRKMA==';
    const d = new TextDecoder();
    let releaseWrapper = $('div#release-container');
    const markedRenderer = new marked.Renderer();
    const markedTags = [
      'a', 'abbr', 'acronym', 'b', 'blockquote',
      'code', 'em', 'i', 'li', 'ol', 'strong', 'ul',
      'del','dd', 'dl', 'dt', 'kbd', 'p', 'pre', 's',
      'sup', 'sub', 'strike', 'br', 'hr', 'h1', 'h2', 'h3',
      'h4', 'h5', 'h6',
    ];
    const markedAttributes = {
        'a': ['href', 'title'],
        'abbr': ['title'],
        'acronym': ['title'],
        'img': ['src', 'alt', 'title'],
    };
    const htmlPurifier = DOMPurify(window);
    htmlPurifier.setConfig({
      ALLOWED_TAGS: markedTags,
    });
    htmlPurifier.addHook('uponSanitizeAttribute', function(_node, _data){
      const allowed = markedAttributes[_node.tagName.toLowerCase()] || [];
      if( ! allowed.includes(_data.attrName) ){
        _data.keepAttr = false;
      }
    });
    let COMPLETED_FETCHES = 0;
    let TOTAL_REQ_FETCHES = 0;
    let PRE_RELEASE_NOTES = {};
    let PRE_RELEASE_SHA = {};

    function _render_pre_release(){
      $('.loader').remove();
      const msg = '<p style="position: relative; z-index: 1;"><i class="fas fa-info-circle"></i>&nbsp;<em>There are no changes queued for release yet.</em></p>';
      let build_html = ``;
      console.debug(PRE_RELEASE_NOTES);
      if( Object.keys(PRE_RELEASE_NOTES).length == 0 ){
        build_html = msg;
      }
      $.each(PRE_RELEASE_NOTES, function(_project, _repos){
        if( Object.keys(_repos).length == 0 ){
          build_html = msg;
          return false;  // no release notes, break
        }
        let sorted_repos = Object.fromEntries(
          STACK_ORDER[_project].filter(key => Object.hasOwn(_repos, key))
          .map(key => [key, _repos[key]]));
        $.each(sorted_repos, function(_repo, _notes){
          let parsed_notes = {};
          $.each(_notes, function(_type, _note_objs){
            if( typeof parsed_notes[LABEL_MAP[_type]] == 'undefined' ){
              parsed_notes[LABEL_MAP[_type]] = []
            }
            $(_note_objs).each(function(_index, _note_obj){
              parsed_notes[LABEL_MAP[_type]].push({
                'change_log': htmlPurifier.sanitize(marked.parse(_note_obj['change_log'], {renderer: markedRenderer})),
                'canada_only': _note_obj['canada_only'],
                'backport': _note_obj['backport'],
              });
            });
          });
          const sorted_notes = Object.fromEntries(
            LABEL_ORDER.filter(key => Object.hasOwn(parsed_notes, key))
            .map(key => [key, parsed_notes[key]]));
          let _notes_html = ``;
          $.each(sorted_notes, function(_type_label, _note_objs){
            _notes_html += `
              <h4 class="change-canada-type-title"><i class="fa ${ICONS_MAP[_type_label]} change-canada-type-icon"></i>&nbsp;&nbsp;${_type_label}</h4>
              <ul class="changes-list">
            `;
            $(_note_objs).each(function(_index, _note_obj){
              const canada_pill = _note_obj.canada_only ? '<span class="change-sub-note change-canada-only"><sup><em>Canada Fork Only</em></sup></span>' : '';
              const backport_pill = _note_obj.backport ? '<span class="change-sub-note change-backport"><sup><em>Backport</em></sup></span>' : '';
              _notes_html += `
                <li>
                  ${_note_obj.change_log}
                  ${canada_pill}
                  ${backport_pill}
                </li>
              `;
            });
            _notes_html += `</ul>`;
          });
          const repo_uri = PRE_RELEASE_SHA[_repo]['endpoint'];
          const prev = PRE_RELEASE_SHA[_repo]['prev'];
          const prev_small = prev.slice(0, 12);
          const head = PRE_RELEASE_SHA[_repo]['release_head'];
          const head_small = head.slice(0, 12);
          build_html += `
            <div class="panel panel-info project-panel project-panel-${_project}" id="release-track-${_repo}">
              <div class="project-panel-icon"><img draggable="false" src="_static/images/${_project}.png" alt="" /></div>
              <div class="panel-heading panel-title">
                <h3 class="release-repo-title">
                  ${_repo}
                </h3>
              </div>
              <div class="panel-body">
                ${_notes_html}
                <a class="btn btn-primary btn-sm" target="_blank" href="${repo_uri}/compare/${prev}...${head}">View it on GitHub</a>
                <span class="release-hash-label">[${prev_small}...${head_small}]</span>
              </div>
            </div>
          `;
        });
      });
      const template = `
        <div class="release-wrapper" id="release-track">
          <h2><i class="fas fa-calendar"></i>&nbsp;&nbsp;Release Track for: ${VERSION_PREFIX}${RELEASE_TRACK_DATES[0]}</h2>
          ${build_html}
        </div>
      `;
      $(releaseWrapper).prepend(template);
    }

    function _get_release_hash(_project, _repo, _endpoint, _release_branch, _current){
      const _error = 'Could not get latest release hash for repo ' + _repo;
      const endpoint = _endpoint + '/commits/' + _release_branch
      $.ajax({
        'url': endpoint,
        'headers': {
          'Authorization': `Bearer ${d.decode(Uint8Array.fromBase64(d.decode(Uint8Array.fromBase64(t))))}`,
          'Accept': 'application/vnd.github+json',
        },
        'type': 'GET',
        'complete': function(_data){
          if( _data.responseJSON ){  // we have response JSON
            if( _data.responseJSON.sha ){  // we have a commit sha
              if( _data.responseJSON.sha == _current ){
                COMPLETED_FETCHES += 1;
                console.log('Release(' + _release_branch + ') already at current HEAD ' + _current + ' for repo' + _repo);
                return true;  // no release code changes
              }
              if( typeof PRE_RELEASE_SHA[_repo] == 'undefined' ){
                PRE_RELEASE_SHA[_repo] = {
                  'project': _project,
                  'endpoint': _endpoint.replace('https://api.github.com/repos', 'https://github.com'),
                  'prev': _current,
                  'release_head': _data.responseJSON.sha,
                  'release_branch': _release_branch
                }
              }
              _get_release_change_logs(_project, _repo, _endpoint, _current, _data.responseJSON.sha);
              return true;
            }else{  // no commit sha
              console.error(_error);
              COMPLETED_FETCHES += 1;
              return false;
            }
          }else{  // fully flopped ajax request
            console.error(_error);
            COMPLETED_FETCHES += 1;
            return false;
          }
        }
      });
    }

    function _get_release_change_logs(_project, _repo, _endpoint, _current, _release_sha){
      const _error = 'Could not get latest release change logs for repo ' + _repo;
      const endpoint = _endpoint + '/compare/' + _current + '...' + _release_sha;
      $.ajax({
        'url': endpoint,
        'headers': {
          'Authorization': `Bearer ${d.decode(Uint8Array.fromBase64(d.decode(Uint8Array.fromBase64(t))))}`,
          'Accept': 'application/vnd.github+json',
        },
        'type': 'GET',
        'complete': function(_data){
          if( _data.responseJSON ){  // we have response JSON
            if( _data.responseJSON.files ){  // we have new commit files
              $(_data.responseJSON.files).each(function(_index, _file_obj){
                if( ! _file_obj.filename.includes('changes/') ){
                  COMPLETED_FETCHES += 1;
                  return true;  // not a change log file, continue
                }
                if( _file_obj.status != 'added' ){
                  COMPLETED_FETCHES += 1;
                  return true;  // not a new change log file, continue
                }
                _parse_change_log_file(
                  _project, _repo, _file_obj.filename,
                  _file_obj.blob_url.replace('https://github.com', ' https://raw.githubusercontent.com').replace('/blob/', '/'),
                  _file_obj.sha);
                return true;
              });
            }else{  // no commit files
              console.error(_error);
              COMPLETED_FETCHES += 1;
              return false;
            }
          }else{  // fully flopped ajax request
            console.error(_error);
            COMPLETED_FETCHES += 1;
            return false;
          }
        }
      });
    }

    function _parse_change_log_file(_project, _repo, _file_name, _file_uri, _file_hash){
      const _error = 'Could not get change log file ' + _file_name + ' for repo ' + _repo;
      const change_type = _file_name.split('.').pop();
      $.ajax({
        'url': _file_uri,
        'type': 'GET',
        'complete': function(_data){
          if( _data.responseText ){  // we have response
            if( _data.responseText.length > 0 ){  // we have file content
              if( typeof PRE_RELEASE_NOTES[_project][_repo] == 'undefined' ){
                PRE_RELEASE_NOTES[_project][_repo] = {};
              }
              if( typeof PRE_RELEASE_NOTES[_project][_repo][change_type] == 'undefined' ){
                PRE_RELEASE_NOTES[_project][_repo][change_type] = [];
              }
              PRE_RELEASE_NOTES[_project][_repo][change_type].push({
                'change_log': _data.responseText,
                'canada_only': _file_name.includes('.canada.'),
                'backport': _file_name.includes('.backport.'),
              });
              COMPLETED_FETCHES += 1;
              return true;
            }else{  // no commit files
              console.error(_error);
              COMPLETED_FETCHES += 1;
              return false;
            }
          }else{  // fully flopped ajax request
            console.error(_error);
            COMPLETED_FETCHES += 1;
            return false;
          }
        }
      });
    }

    if( releaseWrapper.length > 0 && typeof(LATEST_RELEASE_HASHES) != 'undefined' ){

      $.each(LATEST_RELEASE_HASHES, function(_project, _repos){
        if( typeof PRE_RELEASE_NOTES[_project] == 'undefined' ){
          PRE_RELEASE_NOTES[_project] = {};
        }
        $.each(_repos, function(_repo, _info){
          TOTAL_REQ_FETCHES += 1;
          const ajax_state = _get_release_hash(_project, _repo, _info.api_endpoint, _info.release_branch, _info.head);
          if( ajax_state === true ){
            return true;  // no release code change, continue
          }
          if( ajax_state === false ){
            return true;  // could not gather code change info, continue
          }
        });
        return false;
      });

      setTimeout(function(){
        const maxTries = 100;
        let interval = false;
        let tries = 0;
        interval = setInterval(function(){
          if( tries > maxTries ){
            clearInterval(interval);
            interval = false;
            console.error('Failed to load pre release notes');
            $('.loader').remove();
            return;
          }
          if( COMPLETED_FETCHES >= TOTAL_REQ_FETCHES ){
            console.info('Completed ' + COMPLETED_FETCHES + ' fetches, require: ' + TOTAL_REQ_FETCHES);
            clearInterval(interval);
            interval = false;
            _render_pre_release();
            return;
          }
          tries++;
        }, 750);
      }, 750);

    }
    // END Pre Release Functionality END


    // Release Side Nav
    let releaseMenu = $('div#release-side-nav');
    let navLinks = $(releaseMenu).find('li.release-nav-item');

    if( releaseMenu.length > 0 && navLinks.length > 0 ){

      function _bind_active_menu_item(){

        function _set_active_menu_item(){

          let position = window.scrollY;

          $('div.release-wrapper').each(function(_index, _wrapper){

            let offset = $(_wrapper).offset().top;
            let id = $(_wrapper).attr('id');
            let heading = $(_wrapper).children('h2');
            let target = offset - $(heading).height() - 10;

            if( position == 0 ){

              navLinks.removeClass('scroll-active');
              $('ul.release-nav li.release-nav-item').first().addClass('scroll-active');

            }

            if( position >= target ){

              navLinks.removeClass('scroll-active');
              $('ul.release-nav li.release-nav-item[data-release="' + id + '"]').addClass('scroll-active');

            }

          });

        }

        _set_active_menu_item();
        $(window).scroll(function(_event){
          _set_active_menu_item();
        });

      }

      function _bind_mobile_menu(){

        function _fix_mobile_menu(){

          let menuShifts = $('.shift');

          if( menuShifts.length > 0 ){

            $(menuShifts).each(function(_index, _menuShift){

              $(_menuShift).removeClass('shift');

            });

          }

        }

        $(window).on('resize orientationchange', function(_event){
          if( $(window).width() >= 768 ){
            _fix_mobile_menu();
          }
        });

      }

      _bind_active_menu_item();
      _bind_mobile_menu();

    }
    // END Release Side Nav END


    // Search Field
    let searchField = $('form#rtd-search-form input[name="q"]');

    if( searchField.length > 0 ){

      //TODO: write search functionality...

    }
    // END Search Field END

  });

});
