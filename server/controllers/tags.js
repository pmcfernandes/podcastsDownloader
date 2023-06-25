function getTags(req, res) {
    let episode = req.params.guid || '';
    let sql = '';

    if (episode === '') {
        sql = `SELECT genre FROM podcasts`;
    } else {
        sql = `SELECT keywords FROM podcasts_items WHERE guid = '${episode}'`;
    }

    req.db.all(sql, [], (err, rows) => {
        if (err) {
            res.status(404).json({ success: false, data: '404' });
        } else {
            if (rows.length === 0) {
                res.json([]);
            } else {
                let data = rows.map(row => {
                    return row.genre.split(',').map(genre => {
                        return genre.toLowerCase();
                    });
                }).filter((value, index, array) => {
                    return array.indexOf(value) === index;
                });

                res.json(data);
            }
        }
    });
}

function updateTags(req, res) {
    let postData = req.body;
    let id = parseInt(req.params.id);

    let sql = `
        UPDATE podcasts
        SET genre = '${postData.tags.join(', ')}',
        WHERE id = ${id}
    `;

    req.db.run(sql, [], (err) => {
        if (err) {
            res.status(404).json({ success: false, data: '404' });
        } else {
            res.status(200).json({ success: true, data: '200 OK!' });
        }
    });
}

module.exports = { getTags, updateTags };