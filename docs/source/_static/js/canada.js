window.addEventListener('load', function(){

  $(document).ready(function(){

    const urlParams = new URLSearchParams(window.location.search);

    let selectedVersion = urlParams.get('ver');

    let versionSelectForm = $('form#version-select');

    if( versionSelectForm.length > 0 ){

      const currentVersion = $(versionSelectForm).attr('data-current-version');

      if( selectedVersion == null || typeof selectedVersion == 'undefined' ){

        selectedVersion = currentVersion;

      }

      let select = $(versionSelectForm).find('select');
      let options = $(select).find('option');

      if( options.length > 0 ){

        $(options).each(function(_index, _option){

          let value = $(_option).attr('value');

          if( value == selectedVersion ){

            $(_option).attr('selected', 'selected');
            $(select).trigger('change').blur();

          }

        });

      }

      $(select).on('change', function(_event){

        _newValue = $(select).val();

        if( _newValue != selectedVersion ){

          window.location.href = '?ver=' + _newValue;

        }

      });

    }

  });

});
