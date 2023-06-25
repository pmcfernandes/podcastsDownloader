function download(segment) {
    const a = document.createElement("a");

    if (segment.startsWith("http")) {
        a.href = segment;
    } else {
        a.href = url() + (segment.startsWith("/") ? segment : '/' + segment);
    }

    const clickEvnt = new MouseEvent("click", {
        view: window,
        bubbles: true,
        cancelable: true,
    });

    a.dispatchEvent(clickEvnt);
    a.remove();
}

function uuid() {
    return URL.createObjectURL(new Blob([])).slice(-36);
}

export { uuid, download }