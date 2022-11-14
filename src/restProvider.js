
import simpleRestProvider from 'ra-data-simple-rest';
import { fetchUtils } from 'ra-core';

export default (
    apiUrl,
    httpClient = fetchUtils.fetchJson,
    countHeader = 'Content-Range'
) => ({
    ...simpleRestProvider(apiUrl, httpClient, countHeader),

    //Override to use query parameters
    getOne: (resource, params) => {
        //console.log("Fetch", resource);
        return httpClient(`${apiUrl}/${resource}/${params.id}`).then(({ json }) => ({
            data: json,
        }));
    }
});
