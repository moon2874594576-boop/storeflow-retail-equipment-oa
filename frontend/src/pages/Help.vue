<template><div class="page-heading"><div><span class="eyebrow">A LITTLE GUIDANCE</span><h1>让协作更顺畅</h1><p>了解角色分工、流转规则，以及遇到问题时的处理方式。</p></div><router-link to="/requests" class="text-link">进入申请列表 →</router-link></div><section class="help-hero"><Icon name="help" /><div><h2>从申请到归还，一条清晰的时间线。</h2><p>StoreFlow 管理临时设备借用。每张申请只借用一台设备，预计归还日期由申请人填写。</p></div></section><div class="help-role-grid"><article v-for="role in roles" :key="role.name" class="panel"><span class="eyebrow">{{ role.no }}</span><h3>{{ role.name }}</h3><p>{{ role.scope }}</p><ol><li v-for="step in role.steps" :key="step">{{ step }}</li></ol></article></div><section class="panel faq-panel"><div class="panel-heading"><h3>常见问题</h3><span class="muted">FAQ / 日常使用</span></div><el-collapse><el-collapse-item v-for="(faq, index) in faqs" :key="index" :name="index" :title="faq.question"><p>{{ faq.answer }}</p></el-collapse-item></el-collapse></section><section class="panel help-boundary"><Icon name="shield" /><div><h3>关于这个项目</h3><p>这是基于开源 Enterprise OA 改造的学习与工程验证项目。演示使用虚构门店、人员和设备数据，不代表接入任何企业内部系统，也不代表真实生产使用。账户权限和数据由本地服务管理。</p><p>演示前可使用 README 中的账号顺序走完流程；备份、恢复和环境检查方法见项目随附文档。</p></div></section></template>
<script setup>
import Icon from '../ui/Icon.vue'
const roles = [
  { no: '01 / REQUEST', name: '门店员工', scope: '关注自己发起的申请和正在使用的设备。', steps: ['选择类别、填写用途与预计归还日期。', '保存草稿或提交给店长审批。', '当面核对设备编号后确认签收。', '交回设备后申请归还验收。'] },
  { no: '02 / APPROVE', name: '门店店长', scope: '处理所属门店的申请，确认实际业务需要。', steps: ['查看申请用途、设备类别和借用期限。', '通过申请，或填写具体原因驳回。', '关注门店借用中及逾期未归还的设备。'] },
  { no: '03 / HANDOVER', name: '设备管理员', scope: '管理总部设备池，完成发放和归还交接。', steps: ['给已通过申请分配同类别空闲设备。', '未签收前可按实际情况撤销发放。', '验收归还设备，登记正常或存在异常。', '异常设备修复并检查后恢复可用。'] },
  { no: '04 / CONFIGURE', name: '系统管理员', scope: '维护成员与门店，提供清晰的业务权限。', steps: ['创建门店与成员账号，分配业务角色。', '为门店配置店长负责人。', '查看业务记录与统计，不代替业务人员审批。'] },
]
const faqs = [
  { question: '提交后发现填写有误，怎么办？', answer: '提交后的申请不能直接改用途、类别和门店。在设备发放前，可以撤回并重新申请。草稿仍可编辑；已结束的记录会保留，方便追溯。' },
  { question: '审批已通过，为什么还没有设备？', answer: '审批通过表示业务需求已确认，实际设备还需要管理员分配。没有同类别空闲设备时，申请保持待发放，不会虚构设备或提前占用。' },
  { question: '为什么签收前就不能撤回了？', answer: '管理员已登记发放，设备已经进入交接。若尚未实际收到，请联系管理员在待签收阶段撤销发放；已经签收时，通过归还流程结束借用。' },
  { question: '已申请归还，设备为何仍显示占用？', answer: '归还申请需要设备管理员实际收到设备并完成检查。只有验收通过，设备才重新成为空闲；发现异常则进入待维修。' },
  { question: '逾期后还能归还吗？', answer: '可以。逾期只是提醒，不会阻断归还。预计归还日期已过，且仍处于借用中或待归还验收时，会标记逾期。日期按北京时间自然日计算。' },
  { question: '提示“状态已变化”或“设备不可分配”，怎么办？', answer: '可能已有其他人员处理，或设备刚被另一张申请占用。刷新详情，查看最新流转记录，再选择当前允许的操作。不要反复点击提交。' },
  { question: '店长看不到员工的申请，应该检查什么？', answer: '首先确认申请已提交；再检查双方所属门店以及门店负责人配置。跨门店记录不会因为修改页面地址而开放。如有配置问题，请系统管理员处理。' },
  { question: '页面无法加载或登录失败，如何排查？', answer: '确认 main.py 对应的本地服务仍在运行；查看终端提示和随附日志；检查端口是否被占用。账号密码错误、账号停用与服务连接失败会显示不同提示。演示密码可以在初始化时修改，应以实际配置为准。' },
]
</script>
