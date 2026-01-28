<?php

//
// Controller for display
// https://{domain}/community/notice
//
class Notice extends \controller\Make_Controller {

    public function init()
    {
        $this->layout()->category_key(33);
        $this->layout()->head();
        $this->layout()->view();
        $this->layout()->foot();
    }

    public function make(){
        $this->module();
    }

    public function module(){
        $module = new \Module\Board\Make_Controller();
        $module->set('id', 'community_notice');
        $module->run();
    }

}

//
// Controller for display
// https://{domain}/community/pds
//
class Pds extends \controller\Make_Controller {

    public function init()
    {
        $this->layout()->category_key(34);
        $this->layout()->head();
        $this->layout()->view();
        $this->layout()->foot();
    }

    public function make(){
        $this->module();
    }

    public function module(){
        $module = new \Module\Board\Make_Controller();
        $module->set('id', 'community_pds');
        $module->run();
    }

}

//
// Controller for display
// https://{domain}/community/free
//
class Free extends \controller\Make_Controller {

    public function init()
    {
        $this->layout()->category_key(35);
        $this->layout()->head();
        $this->layout()->view();
        $this->layout()->foot();
    }

    public function make(){
        $this->module();
    }

    public function module(){
        $module = new \Module\Board\Make_Controller();
        $module->set('id', 'community_free');
        $module->run();
    }

}

//
// Controller for display
// https://{domain}/community/qna
//
class Qna extends \controller\Make_Controller {

    public function init()
    {
        $this->layout()->category_key(36);
        $this->layout()->head();
        $this->layout()->view();
        $this->layout()->foot();
    }

    public function make(){
        $this->module();
    }

    public function module(){
        $module = new \Module\Board\Make_Controller();
        $module->set('id', 'community_qna');
        $module->run();
    }

}

//
// Controller for display
// https://{domain}/community/link
//
class Link extends \controller\Make_Controller {

    public function init()
    {
        $this->layout()->category_key(37);
        $this->layout()->head();
        $this->layout()->view();
        $this->layout()->foot();
    }

    public function make()
    {
        $this->module();
    }

    public function module()
    {
        $module = new \Module\Contents\Make_Controller();
        $module->set('key', 'sitelink');
        $module->run();
    }

}
