window.addEventListener( 'DOMContentLoaded', () => {
    'use strict';

    document.querySelectorAll( 'img' ).forEach( img => {
        function onClick( click ) {
            if ( click.button === 1 ||
                 click.button === 0 && (
                     click.ctrlKey || click.metaKey
                 ) ) {
                const input = img.closest( 'label' ).querySelector( 'input' ),
                      title = input.value,
                      url = 'https://commons.wikimedia.org/wiki/' +
                      encodeURIComponent( title.replace( / /g, '_' ) );
                window.open( url, '_blank' );
                click.preventDefault();
            }
        }
        img.addEventListener( 'click', onClick );
        img.addEventListener( 'auxclick', onClick );
    } );

    const explanation = document.createElement( 'p' );
    explanation.textContent = 'Middle-click, control-click or command-click an image ' +
        'to open the file description page in a new tab.';
    document.getElementById( 'selection_buttons' ).prepend( explanation );
} );
