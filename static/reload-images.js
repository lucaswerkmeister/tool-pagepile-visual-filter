window.addEventListener( 'DOMContentLoaded', () => {
    'use strict';

    /**
     * Automatically reload images to deal with 429 Too Many Requests errors.
     *
     * As of 28 July 2022, Thumbor allows up to 50 requests to be queued,
     * with a timeout of 4 seconds (https://w.wiki/5WhF).
     * By spacing out the reloads by 100 milliseconds,
     * we ensure that reloads caused by this script fit into this queue
     * (4 seconds / 50 = 80 milliseconds).
     * If the user scrolls quickly, the browser may still lazy-load too many images at once,
     * but because the earliestNextReload is shared between all images
     * and incremented with every error, the reloads should not repeat the burst.
     * On the other hand, because the earliestNextReload is a timestamp, not a delay,
     * if a bunch of images get loaded and then the user waits before scrolling,
     * the new images from the scroll don’t have to wait too long –
     * they’re not penalized by the earlier throttling,
     * there’s no residual exponential backoff.
     */

    let earliestNextReload = 0; // performance.now() clock (milliseconds)

    document.querySelectorAll( 'img' ).forEach( img => {
        img.addEventListener( 'error', () => {
            const now = performance.now();
            earliestNextReload = Math.max( earliestNextReload, now ) + 100;
            setTimeout( () => {
                img.src = img.src; // reload
            }, earliestNextReload - now );
        } );
    } );
} );
