<?php

define('MAINPAGE', TRUE);

//
// Controller for display
// https://{domain}
//
class Index extends \Controller\Make_Controller {

    public function init()
    {
        $this->layout()->head();
        $this->layout()->view(PH_THEME_PATH.'/html/index.tpl.php');
        $this->layout()->foot();
    }

    public function make()
    {

    }

    // 팝업 Fetch
    public function popup_fetch()
    {
        $fetch = new \Controller\Make_View_Fetch();
        $fetch->set('doc', PH_PATH.'/lib/popup.fetch.php');
        $fetch->run();
    }

    // 배너 Fetch
    public function banner_fetch($key)
    {
        $fetch = new \Controller\Make_View_Fetch();
        $fetch->set('doc', PH_PATH.'/lib/banner.fetch.php');
        $fetch->set('key', $key);
        $fetch->run();
    }

    // 공지사항 최근게시물
    public function latest_notice()
    {
        $fetch = new \Controller\Make_View_Fetch();
        $fetch->set('doc', MOD_BOARD_PATH.'/lib/latest.fetch.php');
        $fetch->set('id', 'community_notice');
        $fetch->set('theme', 'basic');
        $fetch->set('orderby', 'recent');
        $fetch->set('limit', 5);
        $fetch->set('subject', 40);
        $fetch->set('uri', PH_DIR.'/community/notice');
        $fetch->run();
    }

    // 행복한이야기 최근게시물
    public function latest_story()
    {
        $fetch = new \Controller\Make_View_Fetch();
        $fetch->set('doc', MOD_BOARD_PATH.'/lib/latest.fetch.php');
        $fetch->set('id', 'story_album');
        $fetch->set('theme', 'gallery');
        $fetch->set('orderby', 'recent');
        $fetch->set('limit', 4);
        $fetch->set('subject', 30);
        $fetch->set('img-width', 200);
        $fetch->set('img-height', 150);
        $fetch->set('uri', PH_DIR.'/story/album');
        $fetch->run();
    }

}
