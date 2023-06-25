function index(req, res) {
    res.status(200).send({
        title: "podcastsDownloader Express API",
        version: "0.5.1"
    });
}

module.exports = { index };