async function get_random_trial() {
    fetch('get_random_trial_id.php')
    .then(response=>response.text())
    .then(data=>{window.location.assign("trial?PMID="+data)})
    .catch(err=>console.log(err));
}
