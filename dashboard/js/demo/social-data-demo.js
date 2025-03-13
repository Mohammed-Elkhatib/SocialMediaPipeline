function updateSocialData() {
    $.ajax({
        url: 'http://127.0.0.1:8000/api/social-media-data',  // API endpoint for random data
        type: 'GET',
        success: function(data) {
            // Update the values in the HTML with the fetched data
            $('#totalLikes').text(data.total_likes.toLocaleString());
            $('#totalFollowers').text(data.total_followers.toLocaleString());
            $('#totalComments').text(data.total_comments.toLocaleString());
            $('#totalShares').text(data.total_shares.toLocaleString());
        },
        error: function(error) {
            console.error('Error fetching data:', error);
        }
    });
}

updateSocialData();