import axios from 'axios';

const api = axios.create({
    baseURL: 'http://localhost:3010/api',
    timeout: 3000,
    responseType: 'json',
    validateStatus: function (status) {
        return status === 200;
    }
})

function doGetRequest(url, params) {
    let promise = new Promise((resolve, reject) => {
        api.get(url, {
            responseType: 'json', 
            ...params
        }).then(res => resolve(res.data)).catch(err => reject(err));
    });

    return promise;
}

export {
    doGetRequest
}