import request from '/@/utils/request';

/**
 * 项目使用接口
 * @method getProjectList 获取项目列表
 * @method getMenuTest 获取后端动态路由菜单(test)
 */
export function userServerIpApi() {
  return {
    getList: (data) => {
      return request({
        url: '/serverip/list',
        method: 'POST',
        data,
      });
    },
    saveOrUpdate(data) {
      return request({
        url: '/serverip/saveOrUpdate',
        method: 'POST',
        data
      })
    },
    deleted: (data) => {
      return request({
        url: '/serverip/deleted',
        method: 'POST',
        data,
      });
    },
    getTree: (data) => {
      return request({
        url: '/serverip/getServerIpTree',
        method: 'POST',
        data,
      });
    },
  };
}
