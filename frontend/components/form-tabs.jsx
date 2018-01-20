import React from 'react'
import { Tab, Tabs, TabList, TabPanel } from 'react-tabs';
import CourseSection from './learning_circle_form/CourseSection';
import LocationSection from './learning_circle_form/LocationSection';
import DayTimeSection from './learning_circle_form/DayTimeSection';
import FinalizeSection from './learning_circle_form/FinalizeSection';
import 'react-tabs/style/react-tabs.css';

export default class FormTabs extends React.Component{
  constructor(props){
    super(props);
    this.state = {};
    this.switchTab = (tab) => this._switchTab(tab);
    this.updateFormData = (data) => this._updateFormData(data);
  }

  _switchTab(tab) {
    this.props.changeTab(tab)
  }

  render() {
    const buttonIcon = this.props.showHelp ? 'fa fa-arrow-right' : 'fa fa-arrow-left'
    const containerClass = this.props.showHelp ? 'half-screen' : 'full-screen'
    return (
      <div className={`form-container ${containerClass}`}>
        <div className='toggleHelp'>
          <button className='p2pu-btn arrow' onClick={this.props.toggleHelp}>
            <i className={buttonIcon} aria-hidden="true"></i>
          </button>
        </div>
        <Tabs selectedIndex={this.props.currentTab} onSelect={this.switchTab} >
          <TabList className='tabs-list'>
            <Tab className='tabs-item'>{this.props.allTabs[0]}</Tab>
            <Tab className='tabs-item'>{this.props.allTabs[1]}</Tab>
            <Tab className='tabs-item'>{this.props.allTabs[2]}</Tab>
            <Tab className='tabs-item'>{this.props.allTabs[3]}</Tab>
          </TabList>

          <TabPanel className='tab-content'>
            <div className='content-container'>
              <h4>Step 1: Select a Course</h4>
              <CourseSection updateFormData={this.props.updateFormData} {...this.props} />
            </div>
          </TabPanel>
          <TabPanel className='tab-content'>
            <div className='content-container'>
              <h4>Step 2: Find a Location</h4>
              <LocationSection updateFormData={this.props.updateFormData} {...this.props} />
            </div>
          </TabPanel>
          <TabPanel className='tab-content'>
            <div className='content-container'>
              <h4>Step 3: Select the Day and Time</h4>
              <DayTimeSection updateFormData={this.props.updateFormData} {...this.props} />
            </div>
          </TabPanel>
          <TabPanel className='tab-content'>
            <div className='content-container'>
              <h4>Step 4: Finalize and Publish</h4>
              <FinalizeSection updateFormData={this.props.updateFormData} {...this.props} />
            </div>
          </TabPanel>
        </Tabs>
      </div>
    );
  }
}
