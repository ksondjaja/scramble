document.addEventListener('DOMContentLoaded', function(){
    var browserwidth = window.innerWidth;
    var sidebar = document.querySelector('#sidebar');
    var hide = document.querySelector('#chevron-left');
    var expand = document.querySelector('#chevron-right');
    var hamburger = document.querySelector('#hamburger');
    var hamburgerclick = 0;

    if(browserwidth >= 768){
        sidebar.style.display = 'none';
        document.querySelector('#sidebar-ghost').style.display = 'none';
        document.querySelector('#menu-expand').style.display = 'block';
        document.querySelector('#menu-expand').style.marginLeft = '10px';
        document.querySelector('.flex').style.marginTop = '0px';
        document.querySelector('#toggle-show').checked = true;
        document.querySelector('#toggle-hide').checked = false;
    }
    if(browserwidth < 768){
        document.querySelector('#toggle-show').checked = false;
        document.querySelector('#toggle-hide').checked = false;
        sidebar.style.display = 'none';
        hamburger.style.color = 'white';
        document.querySelector('.flex').style.marginTop = '0px';
    }

    window.onresize = function(){
        browserwidth = window.innerWidth;
        // console.log(browserwidth);

        if(browserwidth >= 768){
            sidebar.style.display = 'none';
            document.querySelector('#sidebar-ghost').style.display = 'none';
            document.querySelector('#menu-expand').style.display = 'block';
            document.querySelector('#menu-expand').style.marginLeft = '10px';
            document.querySelector('.flex').style.marginTop = '0px';
            document.querySelector('#toggle-show').checked = true;
            document.querySelector('#toggle-hide').checked = false;
        }
        if(window.getComputedStyle(sidebar).display != 'none' && browserwidth < 1000 && browserwidth >= 768){
            document.querySelector('#menu-expand').style.display = 'none';
            document.querySelector('.flex').style.marginTop = '0px';
            document.querySelector('#toggle-show').checked = true;
            document.querySelector('#toggle-hide').checked = false;
        }
        if(window.getComputedStyle(sidebar).display === 'none' && browserwidth < 1000 && browserwidth >= 768){
            document.querySelector('#menu-expand').style.display = 'block';
            document.querySelector('#menu-expand').style.marginLeft = '10px';
            document.querySelector('.flex').style.marginTop = '0px';
            document.querySelector('#toggle-show').checked = false;
            document.querySelector('#toggle-hide').checked = true;
        }
        if(browserwidth < 768){
            document.querySelector('#toggle-show').checked = false;
            document.querySelector('#toggle-hide').checked = false;
            document.querySelector('#menu-expand').style.display = 'block';
            document.querySelector('#menu-expand').style.marginLeft = '10px';
            sidebar.style.display = 'none';
            document.querySelector('#sidebar-ghost').style.display = 'none';
            document.querySelector('.flex').style.marginTop = '0px';
            hamburgerclick = 0;
            hamburger.style.color = 'white';
        }

    }

    expand.onclick = function(event){
        document.querySelector('#toggle-show').checked = true;
        document.querySelector('#toggle-hide').checked = false;
        sidebar.style.display = 'flex';
        document.querySelector('#sidebar-ghost').style.display = 'flex';
        document.querySelector('#menu-expand').style.display = 'none';
        
    };
    expand.onmouseover = function(event){
        event.target.style.color = '#b1dfbb';
    }
    expand.onmouseout = function(event){
        event.target.style.color = 'white';
    }

    hide.onclick = function(event){
        document.querySelector('#toggle-show').checked = false;
        document.querySelector('#toggle-hide').checked = true;
        sidebar.style.display = 'none';
        document.querySelector('#sidebar-ghost').style.display = 'none';
        document.querySelector('#menu-expand').style.display = 'block';
        document.querySelector('#menu-expand').style.marginLeft = '10px';
    };

    hide.onmouseover = function(event){
        event.target.style.color = '#d9d9d9';
    }
    hide.onmouseout = function(event){
        event.target.style.color = 'white';
    }

    hamburger.onclick = function(event){

        document.querySelector('#toggle-show').checked = false;
        document.querySelector('#toggle-hide').checked = false;
        hamburgerclick += 1;

        if(hamburgerclick%2==0){
            sidebar.style.display = 'none';
            hamburger.style.color = 'white';
            document.querySelector('.flex').style.marginTop = '0px';
        }else{
            event.target.style.color = '#222';
            sidebar.style.display = "block";
            document.querySelector('.flex').style.marginTop = sidebar.getBoundingClientRect().bottom + 'px';
            console.log(sidebar.getBoundingClientRect().bottom);
        }
    };
})