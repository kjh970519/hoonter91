<?php

//
// Controller for display
// https://{domain}/basketball/youth
//
class Youth extends \controller\Make_Controller {

    public function init()
    {
        $this->layout()->category_key(20);
        $this->layout()->head();
        $this->layout()->view();
        $this->layout()->foot();
    }

    public function make(){
        $this->module();
    }

    public function module(){
        $module = new \Module\Board\Make_Controller();
        $module->set('id', 'youth_sports');
        $module->run();
    }

}

//
// Controller for display
// https://{domain}/basketball/military
//
class Military extends \controller\Make_Controller {

    public function init()
    {
        $this->layout()->category_key(21);
        $this->layout()->head();
        $this->layout()->view();
        $this->layout()->foot();
    }

    public function make(){
        $this->module();
    }

    public function module(){
        $module = new \Module\Board\Make_Controller();
        $module->set('id', 'military_academy');
        $module->run();
    }

}

//
// Controller for display
// https://{domain}/basketball/bucheon
//
class Bucheon extends \controller\Make_Controller {

    public function init()
    {
        $this->layout()->category_key(22);
        $this->layout()->head();
        $this->layout()->view();
        $this->layout()->foot();
    }

    public function make(){
        $this->module();
    }

    public function module(){
        $module = new \Module\Board\Make_Controller();
        $module->set('id', 'bucheon_college');
        $module->run();
    }

}
