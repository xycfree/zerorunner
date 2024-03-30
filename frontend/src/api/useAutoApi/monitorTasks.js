import request from '/@/utils/request';

/**
 * 项目使用接口
 * @method getProjectList 获取项目列表
 * @method getMenuTest 获取后端动态路由菜单(test)
 */
export function useMonitorTasksApi() {
  return {
    getList: (data) => {
      return request({
        url: '/monitorTasks/list',
        method: 'POST',
        data,
      });
    },
    saveOrUpdate(data) {
      return request({
        url: '/monitorTasks/saveOrUpdate',
        method: 'POST',
        data
      })
    },
    deleted: (data) => {
      return request({
        url: '/monitorTasks/deleted',
        method: 'POST',
        data,
      });
    },
    taskSwitch: (data) => {
      return request({
        url: '/monitorTasks/taskSwitch',
        method: 'POST',
        data,
      });
    },
    checkCrontab: (data) => {
      return request({
        url: '/monitorTasks/checkCrontab',
        method: 'POST',
        data,
      });
    },
    runOnceJob: (data) => {
      return request({
        url: '/monitorTasks/runOnceJob',
        method: 'POST',
        data,
      });
    },
    getTaskCaseInfo: (data) => {
      return request({
        url: '/monitorTasks/getTaskCaseInfo',
        method: 'POST',
        data,
      });
    },
  };
}
