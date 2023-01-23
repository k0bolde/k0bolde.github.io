
// used to size the iframes to the their contents. Call on the iframe's onload.
function resizeIframe(obj) {
    obj.style.height = obj.contentWindow.document.documentElement.scrollHeight + 'px';
}