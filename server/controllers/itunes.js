
/**
 * Search a podcast in iTunes
 */
async function search(req, res) {
    let text = req.query.text || '';

    if (text === '') {
        res.status(404).json({ success: false, data: '404' });
    } else {
        const response = await fetch(`https://itunes.apple.com/search?term=${text}&entity=podcast`);
        const results = await response.json();

        let rows = results['results'].map(result => {
            return {
                id: result.collectionId,
                title: result.collectionName,
                artist: result.artistName,
                genre: result.primaryGenreName,
                rss_url: result.feedUrl,
                image_url: result.artworkUrl600
            }
        });

        res.json(rows);
    }
};

module.exports = { search };    