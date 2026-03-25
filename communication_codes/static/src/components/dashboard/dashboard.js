/** @odoo-module **/

import { registry } from "@web/core/registry";
import { Layout } from "@web/search/layout";
import { getDefaultConfig } from "@web/views/view";
import { useService } from "@web/core/utils/hooks";
import { Component, onWillStart, onMounted, useRef } from "@odoo/owl";
import { _t } from "@web/core/l10n/translation";

export class CommunicationCodesDashboard extends Component {
    setup() {
        this.rpc = useService("rpc");
        this.action = useService("action");
        this.orm = useService("orm");
        
        this.state = {
            stats: {},
            loading: true,
        };

        this.state.last_update = new Date().toLocaleString('ar-LY', {
            hour: '2-digit',
            minute: '2-digit',
            hour12: true
        });

        this.statusChartRef = useRef("statusChart");
        this.systemChartRef = useRef("systemChart");

        onWillStart(async () => {
            await this.loadStats();
        });

        onMounted(() => {
            this.renderCharts();
        });
    }

    async loadStats() {
        const data = await this.orm.call("communication.codes", "get_dashboard_stats", []);
        this.state.stats = data;
        this.state.loading = false;
    }

    renderCharts() {
    if (this.state.loading || !this.statusChartRef.el) return;

    // 1. منطق الضغط على الشارت الدائري (Status Chart)
    const statusCtx = this.statusChartRef.el.getContext('2d');
    new Chart(statusCtx, {
        type: 'doughnut',
        data: {
            labels: [_t('In Stock'), _t('Delivered'), _t('Suspended'), _t('Cancelled')],
            datasets: [{
                data: [
                    this.state.stats.status_counts.in_stock,
                    this.state.stats.status_counts.delivered,
                    this.state.stats.status_counts.suspended,
                    this.state.stats.status_counts.cancelled,
                ],
                backgroundColor: ['#28a745', '#17a2b8', '#ffc107', '#dc3545'],
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            // أضف هذا الجزء للتعامل مع الضغط
            onClick: (evt, activeElements) => {
                if (activeElements.length > 0) {
                    const index = activeElements[0].index;
                    const statusKeys = ['in_stock', 'delivered', 'suspended', 'cancelled'];
                    const clickedStatus = statusKeys[index];
                    this.openView(clickedStatus); // استدعاء الدالة التي تفتح الـ List View
                }
            },
            plugins: {
                legend: { position: 'bottom' }
            }
        }
    });

    // 2. منطق الضغط على شارت الأعمدة (System Chart)
    const systemCtx = this.systemChartRef.el.getContext('2d');
    new Chart(systemCtx, {
        type: 'bar',
        data: {
            labels: [_t('Prepaid'), _t('Monthly Invoice'), _t('Other')],
            datasets: [{
                label: _t('SIMs count'),
                data: [
                    this.state.stats.system_counts.prepaid,
                    this.state.stats.system_counts.monthly_invoice,
                    this.state.stats.system_counts.other,
                ],
                backgroundColor: '#1a414e',
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            // أضف هذا الجزء هنا أيضاً
            onClick: (evt, activeElements) => {
                if (activeElements.length > 0) {
                    const index = activeElements[0].index;
                    const systemKeys = ['prepaid', 'monthly_invoice', 'other'];
                    const clickedSystem = systemKeys[index];
                    this.openSystemView(clickedSystem); // سنحتاج لإنشاء هذه الدالة
                }
            },
            scales: { y: { beginAtZero: true } }
        }
    });
}

async openSystemView(system) {
    await this.action.doAction({
        type: 'ir.actions.act_window',
        name: _t('Communication Codes'),
        res_model: 'communication.codes',
        view_mode: 'list,form',
        views: [[false, 'list'], [false, 'form']],
        domain: [['code_system', '=', system]], // الفلترة حسب النظام
        target: 'current',
    });
}

    async openView(status = false) {
        let domain = [];
        if (status) {
            domain = [['code_status', '=', status]];
        }
        
        await this.action.doAction({
            type: 'ir.actions.act_window',
            name: _t('Communication Codes'),
            res_model: 'communication.codes',
            view_mode: 'list,form',
            views: [[false, 'list'], [false, 'form']],
            domain: domain,
            target: 'current',
        });
    }
}



CommunicationCodesDashboard.template = "communication_codes.Dashboard";
CommunicationCodesDashboard.components = { Layout };

registry.category("actions").add("communication_codes_dashboard", CommunicationCodesDashboard);
