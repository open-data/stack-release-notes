window.addEventListener('load', function(){

  $(document).ready(function(){

    // URL Params
    const urlParams = new URLSearchParams(window.location.search);
    // END URL Params END


    // Release Functionality
    let releaseWrapper = $('div#release-container');

    if( releaseWrapper.length > 0 ){



    }
    // END Release Functionality END


    // Release Side Nav
    let releaseMenu = $('div#release-side-nav');
    let navLinks = $(releaseMenu).find('li.release-nav-item');

    if( releaseMenu.length > 0 && navLinks.length > 0 ){

      function _bind_active_menu_item(){

        function _set_active_menu_item(){

          let position = window.scrollY;

          $('div.release-wrapper').each(function(_index, _wrapper){

            let target = $(_wrapper).offset().top;
            let id = $(_wrapper).attr('id');

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

      _bind_active_menu_item();

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
