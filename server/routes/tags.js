const express = require('express');
const router = express.Router();
const controller = require('../controllers/tags');

router.get('/podcasts', controller.getTags);
router.get('/episodes/:guid', controller.getTags);
router.post('/tags/:id', controller.updateTags);

module.exports = router;