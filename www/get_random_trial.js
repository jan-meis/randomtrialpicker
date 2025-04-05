async function prefetch_next_trial() {
    try {
        const response = await fetch('get_random_trial_id.php');
        const data = await response.text();
        const href = "trial?PMID=" + data; 
        const pageResponse = await fetch(href); // Fetch actual page content
        prefetchedContent = await pageResponse.text(); // Store the page content
        console.log('Page prefetched and stored:', href);
        return [href, prefetchedContent];
    } catch (error) {
        console.error('Error fetching the link:', error);
    }
}

var next_trial = prefetch_next_trial();

async function get_random_trial() {
    const url = await fetch('get_random_trial_id.php')
                      .then(response=>response.text())
                      .then(data=>"trial?PMID="+data)
                      .catch(err=>console.log(err));
    return url;
}
// var next_trial_promise = get_random_trial();
// const next_trial_url = next_trial_promise.then(data => "https://randomtrialpicker.org/" + data);

async function return_random_trial() {
    next_trial.then(data=>{history.pushState(null, "", data[0]); document.open(); document.write(data[1]); document.close();});
}
