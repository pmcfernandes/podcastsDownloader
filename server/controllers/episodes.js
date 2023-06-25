const path = require("path");
const { PODCASTS_PATH } = require('../env');

function getEpisodes(req, res) {
    let page = req.query.page || 1;
    let limit = req.query.limit || 25;
    let id = parseInt(req.params.id);

    let sql = `
        SELECT * 
        FROM podcasts_items 
        WHERE podcast_id = ${id} 
        ORDER BY id ASC 
        LIMIT ${(page - 1) * limit}, ${limit}
    `;

    req.db.all(sql, [], (err, rows) => {
        if (err) {
            res.status(404).json({ success: false, data: '404' });
        } else {
            res.json(rows);
        }
    });
}

function getEpisode(req, res) {
    let id = parseInt(req.params.id);
    let sql = `
        SELECT * 
        FROM podcasts_items 
        WHERE podcast_id = ${id} AND guid = '${req.params.guid}'
    `;

    req.db.all(sql, [], (err, rows) => {
        if (err) {
            res.status(404).json({ success: false, data: '404' });
        } else {
            res.json(rows);
        }
    });
}

function deleteEpisode(req, res) {
    let id = parseInt(req.params.id);

    let sql = `
        DELETE FROM podcasts_items 
        WHERE podcast_id = ${id} AND guid = '${req.params.guid}
    `;

    req.db.all(sql, [], (err, rows) => {
        if (err) {
            res.status(404).json({ success: false, data: '404' });
        } else {
            res.status(200).json({ success: true, data: '200 OK!' });
        }
    });
}

function getMp3Link(req, res) {
    let id = parseInt(req.params.id);

    let sql = `
        SELECT podcasts_items.media_url, podcasts_items.filename  
        FROM podcasts_items 
        WHERE podcast_id = ${id} AND guid = '${req.params.guid}'
    `;

    req.db.all(sql, [], (err, rows) => {
        if (err) {
            res.status(404).json({ success: false, data: '404' });
        } else {
            if (rows.length === 0) {
                res.status(404).json({ success: false, data: '404' });
            } else {
                if (rows[0].downloaded === 0) {
                    res.json({
                        url: rows[0].media_url,
                        remote: true
                    });
                } else {
                    fl = path.join(PODCASTS_PATH, '..', rows[0].filename);

                    if (fs.existsSync(fl)) {
                        res.json({                            
                            url: rows[0].filename.replace('\\', '/'),
                            remote: false
                        });
                    } else {
                        res.json({
                            url: rows[0].media_url,
                            remote: true
                        });
                    }
                }
            }
        }
    });
}


module.exports = { getEpisodes, getEpisode, deleteEpisode, getMp3Link };