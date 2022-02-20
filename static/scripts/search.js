// const searchForm = document.getElementById("search-form")
// searchForm.addEventListener("submit", handleSearch())

// async function handleSearch(event){
//     event.preventDefault();
//     const form = event.currentTarget;
//     const url = form.action;
//     try{
//         const formData = new FormData(form)
//         console.log(`formdata: ${formData}, url: ${url}`)
//     }catch (error){
//         console.log(error)
//     }
// }

// var name = document.getElementById("bookname").value;

function handleSearch(event){
    event.preventDefault();
    const searchKey = document.getElementById("bookname").value;
    fetch(`http://localhost:8000/api/search/books/${searchKey}`).then(response => {response.json}).then(json => {console.log(json)})
    console.log(searchKey);
}