const express = require('express');
const router = express.Router();
const controller = require('../controllers/episodes');

router.get('/:id/episodes', controller.getEpisodes);
router.get('/:id/episodes/:guid', controller.getEpisode);
router.get('/:id/episodes/:guid/mp3', controller.getMp3Link);
router.delete('/:id/episodes/:guid', controller.deleteEpisode);

module.exports = router;